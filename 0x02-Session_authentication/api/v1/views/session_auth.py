#!/usr/bin/env python3
""" Module of Session Auth views
"""


import os
from flask import jsonify, abort
from flask.globals import request
from api.v1.views import app_views
from models.user import User


@app_views.route('/auth_session/login', methods=['POST'], strict_slashes=False)
def session_login():
    """
    Return the dictionary representation of the User
    """
    email = request.form.get('email')
    if email is None or email == "":
        return jsonify({"error": "email missing"}), 400
    password = request.form.get('password')
    if password is None or password == "":
        return jsonify({"error": "password missing"}), 400
    user = User.search(attributes={"email": email})
    if user is None or len(user) == 0:
        return jsonify({"error": "no user found for this email"}), 404
    if not user[0].is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401
    from api.v1.app import auth
    session_id = auth.create_session(user[0].id)
    res = jsonify(user[0].to_json())
    res.set_cookie(os.getenv('SESSION_NAME'), session_id)
    return res


@app_views.route('/auth_session/logout',
                 methods=['DELETE'], strict_slashes=False)
def session_logout():
    """
    Destroys a session
    """
    from api.v1.app import auth
    res = auth.destroy_session(request)
    if not res:
        abort(404)
    return jsonify({}), 200
