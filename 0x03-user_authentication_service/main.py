#!/usr/bin/env python3
"""
End-to-end integration test
"""
import requests


BASE_URL = "http://localhost:5000"


def register_user(email: str, password: str) -> None:
    """Register a new user."""
    res = requests.post(f"{BASE_URL}/users",
                        data={"email": email, "password": password})
    assert res.status_code == 200


def log_in_wrong_password(email: str, password: str) -> None:
    """Attempt to log in with wrong password."""
    res = requests.post(f"{BASE_URL}/sessions",
                        data={"email": email, "password": password})
    assert res.status_code == 401


def log_in(email: str, password: str) -> str:
    """Log in a user and return session ID."""
    res = requests.post(f"{BASE_URL}/sessions",
                        data={"email": email, "password": password})
    assert res.status_code == 200
    session_id = res.cookies.get("session_id")
    return session_id


def profile_unlogged() -> None:
    """Access the user profile without logging in"""
    res = requests.get(f"{BASE_URL}/profile")
    assert res.status_code == 403


def profile_logged(session_id: str) -> None:
    """Access the user profile with the given session ID"""
    headers = {"Cookie": f"session_id={session_id}"}
    res = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert res.status_code == 200
    data = res.json()


def log_out(session_id: str) -> None:
    """Log out the user with the given session ID."""
    headers = {"Cookie": f"session_id={session_id}"}
    res = requests.delete(f"{BASE_URL}/sessions", headers=headers)
    assert res.status_code == 302


def reset_password_token(email: str) -> str:
    """Request a reset password token with the given email."""
    res = requests.post(f"{BASE_URL}/reset_password",
                        data={"email": email})
    assert res.status_code == 200
    data = res.json()
    reset_token = data["reset_token"]
    return reset_token


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Update the user's password with the given reset token."""
    res = requests.put(f"{BASE_URL}/reset_password",
                       data={
                         "email": email,
                         "reset_token": reset_token,
                         "new_password": new_password})
    assert res.status_code == 200


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"

if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
