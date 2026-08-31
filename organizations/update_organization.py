import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, fetch_all
from response import json_response


def lambda_handler(event, context):
    """
    PUT /organizations/{id}
    Body: { "business_name", "default_start_date", "default_end_date" }
    """
    org_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not org_id:
        return json_response(400, {"error": "id is required in the URL path"})

    allowed_fields = ["business_name", "default_start_date", "default_end_date"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return json_response(400, {"error": "no valid fields to update"})

    if "business_name" in updates and not str(updates["business_name"]).strip():
        return json_response(400, {"error": "business_name cannot be empty"})

    if "business_name" in updates:
        updates["business_name"] = updates["business_name"].strip()

    existing = fetch_all("SELECT id FROM organizations WHERE id = %s", (org_id,))
    if not existing:
        return json_response(404, {"error": "organization not found"})

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [org_id]

    updated_row = execute_returning(
        f"UPDATE organizations SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    return json_response(200, updated_row)
