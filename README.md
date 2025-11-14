---

# VAAHAN – AWS-Based Vehicle Rental Platform

**A Cloud-Native Vehicle Rental Marketplace built using AWS Serverless Architecture & React.js**

Vaahan is a fully serverless, scalable, and secure platform that allows users to **list vehicles**, **browse available rentals**, and **book vehicles** in real time.
It integrates **AWS Cognito**, **Lambda**, **API Gateway**, **DynamoDB**, **SNS**, and **CloudFront**, along with an **AI Chatbot powered by IBM Watson Assistant**.

---

## 🌟 Features

### 🔐 **User Authentication**

* Secure login & signup using AWS Cognito
* JWT-based authorization
* Frontend authentication handled by AWS Amplify JS

### 🚘 **Vehicle Listing & Management**

* Add new vehicles via a simple form
* View all available vehicles
* Remove only the vehicles added by logged-in user
* Real-time updates from DynamoDB

### 📝 **Smart Booking System**

* Book a vehicle with atomic DynamoDB operations
* Prevents double-booking using conditional writes
* Sends SNS notifications to the vehicle owner

### ⚙️ **Serverless Backend API**

* REST API built using AWS Lambda + Flask
* API Gateway routes: `/api/vehicles` & `/api/book`
* Fully secured with Cognito JWT verification
* Robust logging with CloudWatch

### 🤖 **AI Chatbot Assistant**

* Integrated IBM Watson Assistant
* Provides live help & guided navigation

---

## 🧱 Architecture Overview

The system follows a fully-serverless event-driven design:

* **Frontend**: React.js hosted on S3 + CloudFront
* **Authentication**: AWS Cognito
* **Backend**: Python (Flask) running inside AWS Lambda
* **API Gateway**: Exposes secure API endpoints
* **Database**: DynamoDB (NoSQL)
* **Notifications**: Amazon SNS
* **Monitoring**: CloudWatch
* **AI Assistant**: IBM Watson Assistant

---

## 📂 Project Structure

```
/frontend
    ├── src
    │   ├── components
    │   ├── pages
    │   └── App.js
/backend
    ├── app.py
    ├── lambda_function.py
    └── requirements.txt
/docs
    └── AWS_VAAHAN_Project_Report.pdf
```

---

## 🚀 Live Demo

**Frontend (CloudFront):**
🔗 [https://d2y5ak3q65zpz1.cloudfront.net/](https://d2y5ak3q65zpz1.cloudfront.net/)

**GitHub Repository:**
🔗 [https://github.com/SushenGrover/VAAHAN-aws-based-vehicle-rental-platform](https://github.com/SushenGrover/VAAHAN-aws-based-vehicle-rental-platform)

---

## 💻 Tech Stack

### **Frontend**

* React.js
* Tailwind CSS
* AWS Amplify (for Auth)
* CloudFront CDN

### **Backend**

* Python Flask
* AWS Lambda
* DynamoDB
* SNS for notifications
* API Gateway

### **Cloud**

* AWS IAM
* AWS S3
* AWS CloudWatch
* IBM Watson Assistant

---

## 🛠️ How to Run Locally

### 1️⃣ Clone the repository

```bash
git clone https://github.com/SushenGrover/VAAHAN-aws-based-vehicle-rental-platform.git
cd VAAHAN-aws-based-vehicle-rental-platform
```

### 2️⃣ Install and run the frontend

```bash
cd frontend
npm install
npm start
```

### 3️⃣ Backend local setup (Optional)

Since the backend is serverless, deployment happens via Lambda.
To run locally, use Flask:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

---

## 📸 Screenshots

* Login Page
* Dashboard
* Add Vehicle Form
* Booking Page
* Profile Page

---

## 🧾 Project Report

The complete detailed architecture & implementation report:
📄 **AWS_VAAHAN_Project_Report.pdf** (included in repo)

---

## 👤 Author

**Sushen Grover**
Reg No: 23BCE1728
B.Tech CSE, VIT Chennai

---

## ⭐ If you like this project…

Please **star ⭐ the repository** on GitHub!

