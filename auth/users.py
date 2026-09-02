import os

from auth.passwords import verify_password


def _user(username_key, password_hash_key, org_id_key, role):
    username = (os.environ.get(username_key) or "").strip()
    password_hash = (os.environ.get(password_hash_key) or "").strip()
    org_id = (os.environ.get(org_id_key) or "").strip()
    if not username or not password_hash or not org_id:
        return None
    return {
        "username": username,
        "password_hash": password_hash,
        "organization_id": int(org_id),
        "role": role,
    }


def configured_users():
    users = []
    demo = _user("DEMO_USERNAME", "DEMO_PASSWORD_HASH", "DEMO_ORG_ID", "demo")
    client = _user("CLIENT_USERNAME", "CLIENT_PASSWORD_HASH", "CLIENT_ORG_ID", "client")
    if demo:
        users.append(demo)
    if client:
        users.append(client)
    return users


def authenticate(username, password):
    if not username or not password:
        return None
    requested = username.strip()
    for user in configured_users():
        if requested.lower() != user["username"].lower():
            continue
        if verify_password(password, user["password_hash"]):
            return user
    return None
