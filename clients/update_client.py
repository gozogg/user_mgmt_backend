import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning
from response import json_response


def lambda_handler(event, context):
    """
    PUT /clients/{id}
    """
    client_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not client_id:
        return json_response(400, {"error": "id is required in the URL path"})

    # Build the SET clause dynamically based on which fields were sent.
    # This keeps the endpoint flexible (e.g. status-only updates) without
    # needing a separate handler for every possible field combination.
    allowed_fields = ["address", "first_name", "last_name", "phone_number", "email"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return json_response(400, {"error": "no valid fields to update"})

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [client_id]

    updated_row = execute_returning(
        f"UPDATE clients SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    if not updated_row:
        return json_response(404, {"error": "client not found"})

    return json_response(200, updated_row)