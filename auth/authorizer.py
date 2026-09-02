import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import jwt

from auth.tokens import decode_token


def _policy(principal_id, effect, resource, context=None):
    statement = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource,
                }
            ],
        },
    }
    if context:
        statement["context"] = context
    return statement


def _wildcard_resource(method_arn):
    # arn:aws:execute-api:region:account:api-id/stage/verb/path
    parts = method_arn.split("/")
    if len(parts) < 2:
        return method_arn
    return f"{parts[0]}/{parts[1]}/*/*"


def lambda_handler(event, context):
    """
    API Gateway TOKEN authorizer.
    Expects Authorization: Bearer <jwt>
    """
    method_arn = event.get("methodArn") or "*"
    resource = _wildcard_resource(method_arn)
    token_header = event.get("authorizationToken") or ""
    secret = os.environ.get("JWT_SECRET")

    if not secret:
        raise Exception("Unauthorized")

    token = token_header
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    else:
        token = token.strip()

    if not token:
        raise Exception("Unauthorized")

    try:
        payload = decode_token(token, secret)
    except jwt.ExpiredSignatureError:
        raise Exception("Unauthorized")
    except jwt.InvalidTokenError:
        raise Exception("Unauthorized")

    username = payload.get("sub")
    org_id = payload.get("org_id")
    role = payload.get("role")
    if not username or org_id is None or not role:
        raise Exception("Unauthorized")

    return _policy(
        str(username),
        "Allow",
        resource,
        {
            "username": str(username),
            "organization_id": str(org_id),
            "role": str(role),
        },
    )
