from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from models.user import User, users_db

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
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.find_by_email(email)
    
    if not user or user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }
    }), 200