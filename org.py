from db import fetch_all
from response import json_response


def _authorizer(event):
    request_context = event.get("requestContext") or {}
    return request_context.get("authorizer") or {}


def get_auth_role(event):
    return str(_authorizer(event).get("role") or "").strip().lower()


def get_auth_username(event):
    return str(_authorizer(event).get("username") or "").strip()


def parse_organization_id(event, body=None):
    """Organization always comes from the JWT authorizer, never from the client."""
    org_id = _authorizer(event).get("organization_id")
    if org_id is None:
        return None, json_response(401, {"error": "unauthorized"})

    try:
        return int(org_id), None
    except (TypeError, ValueError):
        return None, json_response(401, {"error": "unauthorized"})


def require_organization(event, body=None):
    org_id, err = parse_organization_id(event, body)
    if err:
        return None, err

    rows = fetch_all("SELECT id FROM organizations WHERE id = %s", (org_id,))
    if not rows:
        return None, json_response(404, {"error": f"organization {org_id} not found"})

    return org_id, None


def require_client_role(event):
    if get_auth_role(event) != "client":
        return json_response(403, {"error": "only the client account can do this"})
    return None
