from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
import hashlib

users = []

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
    parser.add_argument('password', type=str, required=True, help='Password cannot be blank')

    def post(self):
        data = UserRegister.parser.parse_args()
        if any(user['username'] == data['username'] for user in users):
            return {'message': 'User already exists'}, 400
        hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
        users.append({'username': data['username'], 'password': hashed_password})
        return {'message': 'User created successfully'}, 201

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
    parser.add_argument('password', type=str, required=True, help='Password cannot be blank')

    def post(self):
        data = UserLogin.parser.parse_args()
        user = next((user for user in users if user['username'] == data['username']), None)
        if user and user['password'] == hashlib.sha256(data['password'].encode()).hexdigest():
            access_token = create_access_token(identity=user['username'])
            return {'access_token': access_token}, 200
        return {'message': 'Invalid credentials'}, 401