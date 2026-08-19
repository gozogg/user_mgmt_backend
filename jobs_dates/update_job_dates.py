import json
import sys
import os
from db import execute_returning
from response import json_response

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    PUT /jobs-dates/{id}/{date}
    """
    job_id = event.get("pathParameters", {}).get("id")
    old_date = event.get("pathParameters", {}).get("date")
    body = json.loads(event.get("body") or "{}")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    if not old_date:
        return json_response(400, {"error": "date is required in the URL query"})

    # Build the SET clause dynamically based on which fields were sent.
    # This keeps the endpoint flexible (e.g. status-only updates) without
    # needing a separate handler for every possible field combination.
    allowed_fields = ["date", "status"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return json_response(400, {"error": "no valid fields to update"})

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [job_id] + [old_date]

    updated_row = execute_returning(
        f"UPDATE job_dates SET {set_clause} WHERE job_id = %s AND date = %s RETURNING *",
        values,
    )

    if not updated_row:
        return json_response(404, {"error": "job not found"})

    

    return json_response(200, updated_row)


if __name__ == "__main__":
    fake_event = {
        "pathParameters": {"id": "2"},
        "body": json.dumps({"description": "grass_cut"}),
    }
    result = lambda_handler(fake_event, None)
    print(result)