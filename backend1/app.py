# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import boto3
import uuid
import time
import json
from boto3.dynamodb.conditions import Key
from jwt import decode as jwt_decode, get_unverified_header
from jwt.algorithms import RSAAlgorithm
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__)

# === AWS Cognito config ===
COGNITO_POOL_ID = "ap-south-1_xgbeASCz8"
CLIENT_ID = "33ialm829k69ujoprcdcmk7phu"
REGION = "ap-south-1"
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()

# === DynamoDB & SNS setup ===
dynamodb = boto3.resource("dynamodb", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)
TABLE_NAME = "VaahanVehicles"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:354918362762:vaahan-notifications"

# === Flask CORS setup ===
# === Flask CORS setup ===
FRONTEND_URL = "https://d2y5ak3q65zpz1.cloudfront.net" # <-- Define your CloudFront URL here

CORS(
    app,
    resources={r"/api/*": {"origins": FRONTEND_URL}}, # <-- Restrict to your frontend
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)

# -------------------------------
# Helper: Verify Cognito token
# -------------------------------
def verify_cognito_token(token):
    try:
        headers = get_unverified_header(token)
        key = next(k for k in JWKS["keys"] if k["kid"] == headers["kid"])
        public_key = RSAAlgorithm.from_jwk(key)
        decoded = jwt_decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
        )
        return decoded
    except Exception as e:
        print("Token verification error:", e)
        raise

# -------------------------------
# ⭐️ UPDATED: /api/vehicles
# -------------------------------
@app.route("/api/vehicles", methods=["GET", "POST", "DELETE", "OPTIONS"])
def handle_vehicles():
    
    if request.method == "OPTIONS":
        return jsonify({"status": "CORS preflight OK"}), 200

    # --- Secure all methods ---
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401
    
    token = auth_header.split(" ")[-1]

    try:
        user_info = verify_cognito_token(token)
        username = user_info.get("username") or user_info.get("email") or user_info.get("sub")
    
    except ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except InvalidTokenError as e:
        print("JWT verification failed:", str(e))
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        print("Error verifying token:", e)
        return jsonify({"error": str(e)}), 500

    table = dynamodb.Table(TABLE_NAME)

    # --- Handle GET ---
    if request.method == "GET":
        try:
            resp = table.scan() 
            items = resp.get("Items", [])
            return jsonify({"user": username, "vehicles": items}), 200
        except Exception as e:
            print("Error fetching vehicles:", e)
            return jsonify({"error": str(e)}), 500

    # --- Handle POST (Adding a new vehicle) ---
    if request.method == "POST":
        try:
            body = request.get_json()
            model = body.get("model")
            vehicle_type = body.get("vehicle") or body.get("vehicleType") or body.get("type")
            status = body.get("status", "Active") 

            if not model or not vehicle_type:
                return jsonify({"error": "Missing fields"}), 400

            new_id = str(uuid.uuid4())
            item = {
                "user": username, # This is the Partition Key
                "vehicleId": new_id, # This is NOW the Sort Key
                "model": model,
                "vehicle": vehicle_type,
                "status": status,
                "createdAt": int(time.time()),
            }

            table.put_item(Item=item)
            
            resp = table.scan()
            return jsonify({"user": username, "vehicles": resp.get("Items", [])}), 201

        except Exception as e:
            app.logger.exception("Error adding vehicle")
            return jsonify({"error": str(e)}), 500

    # --- ⭐️ NEW: Handle DELETE ---
    if request.method == "DELETE":
        try:
            body = request.get_json()
            lister_email = body.get("user")
            vehicle_id = body.get("vehicleId")

            # Security check: Make sure the person deleting is the person who listed it
            if username != lister_email:
                return jsonify({"error": "Forbidden: You do not own this vehicle"}), 403

            # We now delete using the full composite key
            table.delete_item(
                Key={
                    'user': lister_email,
                    'vehicleId': vehicle_id
                }
            )
            
            resp = table.scan() # Return the new list
            return jsonify({"user": username, "vehicles": resp.get("Items", [])}), 200

        except Exception as e:
            app.logger.exception("Error deleting vehicle")
            return jsonify({"error": str(e)}), 500

# -------------------------------
# ⭐️ FIXED: POST /api/book
# -------------------------------
@app.route("/api/book", methods=["POST", "OPTIONS"])
def book_vehicle():

    if request.method == "OPTIONS":
        return jsonify({"status": "CORS preflight OK"}), 200
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401
    
    token = auth_header.split(" ")[-1]

    try:
        booker_info = verify_cognito_token(token)
        booker_username = booker_info.get("username") or booker_info.get("email") or booker_info.get("sub")
        
        body = request.get_json()
        lister_email = body.get("listerEmail") 
        vehicle_id = body.get("vehicleId")
        model = body.get("model")

        if not lister_email or not vehicle_id:
            return jsonify({"error": "Missing listerEmail or vehicleId"}), 400
        
        table = dynamodb.Table(TABLE_NAME)

        # --- ⭐️ THIS IS THE FIX ⭐️ ---
        # The Key MUST include both the Partition Key ('user') and the Sort Key ('vehicleId')
        try:
            table.update_item(
                Key={
                    'user': lister_email,
                    'vehicleId': vehicle_id
                },
                UpdateExpression="SET #st = :s, bookedBy = :b",
                ConditionExpression="#st = :av", # Make sure it's still 'Active'
                ExpressionAttributeNames={
                    '#st': 'status'
                },
                ExpressionAttributeValues={
                    ':s': 'Booked',
                    ':b': booker_username,
                    ':av': 'Active' 
                }
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            app.logger.warn("Conditional check failed, vehicle already booked")
            return jsonify({"error": "Vehicle is no longer available"}), 409 # 409 Conflict

        # --- End Fix ---

        # Send SNS notification to the lister
        try:
            sns_message = f"Your vehicle '{model}' was just booked by {booker_username}!"
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps({"default": sns_message}),
                MessageStructure="json",
                Subject="VAAHAN: Your Vehicle Was Booked!"
            )
        except Exception as sns_error:
            print(f"Failed to send SNS message: {sns_error}")
        
        resp = table.scan()
        items = resp.get("Items", [])
        return jsonify({"user": booker_username, "vehicles": items}), 200

    except Exception as e:
        app.logger.exception("Error booking vehicle")
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Run the app locally
# -------------------------------
# if __name__ == "__main__":
#     app.run(debug=True, port=5000)