from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"


def create_token(username, organization_id, role, secret, hours=12):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "org_id": int(organization_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=hours),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_token(token, secret):
    return jwt.decode(token, secret, algorithms=[ALGORITHM])
