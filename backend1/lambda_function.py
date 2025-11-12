# lambda_function.py
import aws_lambda_wsgi
from app import app # Imports the 'app' variable from your app.py

def handler(event, context):
    return aws_lambda_wsgi.handle(app, event, context)