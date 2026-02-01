from flask import Flask, request, jsonify
from src.auth_service import AuthService

app = Flask(__name__)
auth_service = AuthService()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    success, msg = auth_service.register_user(data)
    return jsonify({"success": success, "message": msg}), 200 if success else 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    success, msg, user = auth_service.login_user(email, password)
    
    if success:
        return jsonify({"success": True, "message": msg, "user_name": user.get('full_name')}), 200
    else:
        return jsonify({"success": False, "message": msg}), 401

@app.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    success, msg = auth_service.verify_email(email, otp)
    return jsonify({"success": success, "message": msg}), 200 if success else 400

@app.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.json
    email = data.get('email')
    success, msg = auth_service.resend_verification_otp(email)
    return jsonify({"success": success, "message": msg}), 200 if success else 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
