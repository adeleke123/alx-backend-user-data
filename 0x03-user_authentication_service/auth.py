#!/usr/bin/env python3
"""
Authentication module
"""

import bcrypt
from db import DB
from user import User
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
import uuid


def _hash_password(password: str) -> bytes:
    """Hashes the given password using bcrypt
    Args:
        password (str): The password to hash
    Returns:
        bytes: The hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def _generate_uuid() -> str:
    """Generates a new UUID and returns it as a string.
    Returns:
        str: The generated UUID as a string
    """
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self) -> None:
        """Initialize a new instance of the Auth class."""
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user with the provided email and password
        Args:
            email (str): The new user's email address.
            password (str): The new user's password.
        Returns:
            User: The user object representing the newly created user.
        Raises:
            ValueError: If a user with the given email already exists.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            hashed = _hash_password(password)
            usr = self._db.add_user(email, hashed)
            return usr
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """Validates the login credentials for a user
        Args:
            email (str): The email of the user.
            password (str): The password of the user.
        Returns:
            bool: True if the credentials are correct, otherwise False.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_password = user.hashed_password
        passwd = password.encode("utf-8")
        return bcrypt.checkpw(passwd, user_password)

    def create_session(self, email: str) -> Union[None, str]:
        """Creates a session for a user with the provided email.
        Args:
            email (str): The user's email address.
        Returns:
            Union[None, str]: session ID if the user is found, None otherwise
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self._db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id):
        """Find a user by session ID and return the corresponding User object.
        Args:
            session_id: The session ID to search for.
        Returns:
        Union[User, None]: corresponding User object if found, None otherwise
        """
        user = None
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None
        return user

    def destroy_session(self, user_id: int) -> None:
        """Destroy a user's session by providing the user_id.
        Args:
            user_id (int): ID of user whose session needs to be destroyed
        Returns:
            None
        """
        if user_id is None:
            return None
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Generate a reset password token for a user with the provided email.
        Args:
            email (str): The email of the user.
        Returns:
            str: The generated reset password token.
        Raises:
            ValueError: If the user with the provided email is not found.
        """
        user = None
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError('User not found')
        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Update user's password by providing reset token & new password
        Args:
            reset_token (str): The reset token for the user.
            password (str): The new password for the user.
        Returns:
            None
        Raises:
            ValueError: If the reset token is invalid.
        """
        user = None
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError('Invalid reset token')
        hashed_password = _hash_password(password)
        self._db.update_user(
            user.id,
            hashed_password=hashed_password,
            reset_token=None)
