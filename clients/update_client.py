import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning


def lambda_handler(event, context):
    """
    PUT /clients/{id}
    """
    client_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not client_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id is required in the URL path"})}

    # Build the SET clause dynamically based on which fields were sent.
    # This keeps the endpoint flexible (e.g. status-only updates) without
    # needing a separate handler for every possible field combination.
    allowed_fields = ["address", "first_name", "last_name", "phone_number", "email"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return {"statusCode": 400, "body": json.dumps({"error": "no valid fields to update"})}

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [client_id]

    updated_row = execute_returning(
        f"UPDATE clients SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    if not updated_row:
        return {"statusCode": 404, "body": json.dumps({"error": "client not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(updated_row, default=str),
    }