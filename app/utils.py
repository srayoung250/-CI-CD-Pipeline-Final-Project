from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import request, jsonify, current_app
from jose import jwt, JWTError

ALGORITHM = "HS256"


def _secret_key():
    return current_app.config["SECRET_KEY"]


def encode_token(customer_id):
    """Build a JWT for a customer."""
    payload = {
        "sub": str(customer_id),
        "role": "customer",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def encode_mechanic_token(mechanic_id):
    """Build a JWT for a mechanic, tagged with role=mechanic."""
    payload = {
        "sub": str(mechanic_id),
        "role": "mechanic",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def token_required(f):
    """Validates a customer token and passes customer_id into the wrapped function."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Missing Bearer token"}), 401

        try:
            payload = jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])
        except JWTError:
            return jsonify({"error": "Invalid or expired token"}), 401

        if payload.get("role") != "customer":
            return jsonify({"error": "Customer token required"}), 403

        customer_id = int(payload["sub"])
        return f(customer_id, *args, **kwargs)

    return decorated


def mechanic_token_required(f):
    """Validates a mechanic token and passes mechanic_id into the wrapped function."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Missing Bearer token"}), 401

        try:
            payload = jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])
        except JWTError:
            return jsonify({"error": "Invalid or expired token"}), 401

        if payload.get("role") != "mechanic":
            return jsonify({"error": "Mechanic token required"}), 403

        mechanic_id = int(payload["sub"])
        return f(mechanic_id, *args, **kwargs)

    return decorated
