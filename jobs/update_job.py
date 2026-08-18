import json
import sys
import os
from db import execute_returning

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    PUT /jobs/{id}
    """
    job_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id is required in the URL path"})}

    # Build the SET clause dynamically based on which fields were sent.
    # This keeps the endpoint flexible (e.g. status-only updates) without
    # needing a separate handler for every possible field combination.
    allowed_fields = ["client_id", "frequency", "description", "day_of_week", "price", "start_date", "end_date"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return {"statusCode": 400, "body": json.dumps({"error": "no valid fields to update"})}

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [job_id]

    updated_row = execute_returning(
        f"UPDATE jobs SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    if not updated_row:
        return {"statusCode": 404, "body": json.dumps({"error": "job not found"})}

    

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(updated_row, default=str),
    }


if __name__ == "__main__":
    fake_event = {
        "pathParameters": {"id": "2"},
        "body": json.dumps({"description": "grass_cut"}),
    }
    result = lambda_handler(fake_event, None)
    print(result)