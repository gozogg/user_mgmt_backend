import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    PUT /job-dates/{id}/{date}
    """
    job_id = event.get("pathParameters", {}).get("id")
    old_date = event.get("pathParameters", {}).get("date")
    body = json.loads(event.get("body") or "{}")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    if not old_date:
        return json_response(400, {"error": "date is required in the URL query"})

    org_id, err = require_organization(event, body)
    if err:
        return err

    job_rows = fetch_all(
        "SELECT id FROM jobs WHERE id = %s AND organization_id = %s",
        (job_id, org_id),
    )
    if not job_rows:
        return json_response(404, {"error": "job not found"})

    allowed_fields = ["date", "status"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return json_response(400, {"error": "no valid fields to update"})

    if "status" in updates and updates["status"] not in ("not_complete", "complete", "invoiced"):
        return json_response(400, {
            "error": "status must be not_complete, complete, or invoiced",
        })

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [job_id, old_date, org_id]

    updated_row = execute_returning(
        f"""
        UPDATE job_dates SET {set_clause}
        WHERE job_id = %s AND date = %s AND organization_id = %s
        RETURNING *
        """,
        values,
    )

    if not updated_row:
        return json_response(404, {"error": "job not found"})

    return json_response(200, updated_row)
