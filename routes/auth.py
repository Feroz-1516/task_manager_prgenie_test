from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not all([email, password, name]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if User.find_by_email(email):
        return jsonify({'error': 'User already exists'}), 409
    
    user = User(email=email, password=password, name=name)
    user.save()
    
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({'message': 'User registered successfully', 'token': token, 'user': user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({'message': 'Login successful', 'token': token, 'user': user.to_dict()}), 200

from middleware.auth import token_required

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    token = jwt.encode({
        'user_id': current_user['user_id'],
        'email': current_user['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200
