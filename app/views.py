from app import app, store
from .models import User, Business, Review
from flask import jsonify, request, session
from .exceptions import DuplicationError
import json


@app.route('/api/v1/auth/register', methods = ['POST'])
def register ():
    data = json.loads(request.data.decode('utf-8'))
    user = User.create_user (data)

    try:
        msg = store.add (user)
    except DuplicationError as e:
        return jsonify({'msg': e.msg}), 401

    return jsonify ({"msg": msg}), 200


@app.route ('/api/v1/auth/login', methods = ['POST'])
def login ():
    login_data = json.loads(request.data.decode('utf-8'))
    username = login_data['username']

    target_user = store.users.get(username)

    if not target_user or not target_user.password == login_data['password']:
        return jsonify ({"msg": "Invalid username or password"}), 401

    session['user'] = username
    msg = "logged in {}".format(username)
    return jsonify({'msg': msg}), 200


@app.route ('/api/v1/auth/logout', methods = ['POST'])
def logout ():
    if session.get('user'):
        session.pop('user')
        return jsonify({"msg": "logged out successfully!"}), 200

    return jsonify({"msg": "Unsuccessful!"}), 400


@app.route ('/api/v1/businesses', methods = ['GET', 'POST'])
def businesses ():
    if request.method == 'POST':
        business_data = json.loads (request.data.decode('utf-8'))
        business = Business.create_business (business_data)

        try:
            msg = store.add (business)
        except DuplicationError as e:
            return jsonify ({"msg": e.msg}), 401

        return jsonify ({"msg": msg}), 201

    businesses_info = store.get_businesses_info ()
    return jsonify ({"businesses": businesses_info}), 200


@app.route ('/api/v1/businesses/<int:business_id>', methods = ['GET', 'PUT', 'DELETE'])
def business (business_id):
    business_id = Business.gen_id_string (business_id)
    business_info = store.get_business_info (business_id)
    return jsonify ({"business": business_info}), 200
