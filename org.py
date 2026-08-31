from db import fetch_all
from response import json_response


def parse_organization_id(event, body=None):
    query_params = event.get("queryStringParameters") or {}
    org_id = query_params.get("organization_id")

    if org_id is None and body is not None:
        org_id = body.get("organization_id")

    if org_id is None:
        return None, json_response(400, {"error": "organization_id is required"})

    try:
        return int(org_id), None
    except (TypeError, ValueError):
        return None, json_response(400, {"error": "organization_id must be an integer"})


def require_organization(event, body=None):
    org_id, err = parse_organization_id(event, body)
    if err:
        return None, err

    rows = fetch_all("SELECT id FROM organizations WHERE id = %s", (org_id,))
    if not rows:
        return None, json_response(404, {"error": f"organization {org_id} not found"})

    return org_id, None
