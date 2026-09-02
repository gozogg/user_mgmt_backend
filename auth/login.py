import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from auth.tokens import create_token
from auth.users import authenticate
from response import json_response

JWT_EXPIRES_HOURS = 12


def lambda_handler(event, context):
    """
    POST /login
    Body: { "username", "password" }
    """
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return json_response(400, {"error": "invalid JSON body"})

    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return json_response(400, {"error": "username and password are required"})

    secret = os.environ.get("JWT_SECRET")
    if not secret:
        return json_response(500, {"error": "JWT_SECRET is not configured"})

    user = authenticate(username, password)
    if not user:
        return json_response(401, {"error": "invalid username or password"})

    token = create_token(
        username=user["username"],
        organization_id=user["organization_id"],
        role=user["role"],
        secret=secret,
        hours=JWT_EXPIRES_HOURS,
    )

    return json_response(
        200,
        {
            "token": token,
            "token_type": "Bearer",
            "expires_in": JWT_EXPIRES_HOURS * 3600,
            "user": {
                "username": user["username"],
                "role": user["role"],
                "organization_id": user["organization_id"],
            },
        },
    )
