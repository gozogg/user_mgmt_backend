import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    PUT /organizations/{id}
    Body: { "business_name", "default_start_date", "default_end_date", "alert_days", "alert_email" }
    """
    org_id, err = require_organization(event)
    if err:
        return err

    path_id = (event.get("pathParameters") or {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not path_id:
        return json_response(400, {"error": "id is required in the URL path"})

    try:
        if int(path_id) != org_id:
            return json_response(403, {"error": "forbidden"})
    except (TypeError, ValueError):
        return json_response(400, {"error": "id must be an integer"})

    allowed_fields = ["business_name", "default_start_date", "default_end_date", "alert_days", "alert_email"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    print("updates", updates)

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


if __name__ == "__main__":
    lambda_handler({
        "pathParameters": {
            "id": "1"
        },
        "body": json.dumps({
            "default_start_date": "2026-01-01",
            "default_end_date": "2026-09-30",
        })
    }, {})