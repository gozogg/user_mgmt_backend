import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute, fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    DELETE /job-dates/{id}/{date}
    """
    job_id = event.get("pathParameters", {}).get("id")
    date = event.get("pathParameters", {}).get("date")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    if not date:
        return json_response(400, {"error": "date is required in the URL path"})

    org_id, err = require_organization(event)
    if err:
        return err

    job_rows = fetch_all(
        "SELECT id FROM jobs WHERE id = %s AND organization_id = %s",
        (job_id, org_id),
    )
    if not job_rows:
        return json_response(404, {"error": "job not found"})

    execute(
        """
        DELETE FROM job_dates
        WHERE job_id = %s AND date = %s AND organization_id = %s
        """,
        (job_id, date, org_id),
    )

    return json_response(204)
