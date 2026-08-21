import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from response import json_response

JOBS_SELECT = """
    SELECT
        j.*,
        c.first_name,
        c.last_name,
        c.address,
        c.city
    FROM jobs j
    JOIN clients c ON c.id = j.client_id
"""


def lambda_handler(event, context):
    """
    GET /jobs
    GET /jobs?client_id
    GET /jobs?job_id
    """
    query_params = event.get("queryStringParameters") or {}
    client_id = query_params.get("client_id")
    job_id = query_params.get("job_id")

    if job_id:
        rows = fetch_all(
            JOBS_SELECT + " WHERE j.id = %s",
            (job_id,),
        )
    elif client_id:
        rows = fetch_all(
            JOBS_SELECT + " WHERE j.client_id = %s ORDER BY j.start_date DESC",
            (client_id,),
        )
    else:
        rows = fetch_all(
            JOBS_SELECT + " ORDER BY j.start_date DESC",
        )

    return json_response(200, rows)
