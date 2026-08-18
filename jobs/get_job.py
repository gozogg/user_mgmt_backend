import json
import sys
import os
from db import fetch_all

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    GET /jobs
    """
    query_params = event.get("queryStringParameters") or {}
    # status_filter = query_params.get("status")

    # if status_filter:
    #     rows = fetch_all(
    #         "SELECT * FROM applications WHERE status = %s ORDER BY date_applied DESC",
    #         (status_filter,),
    #     )
    # else:
    rows = fetch_all("SELECT * FROM jobs")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(rows, default=str),  # default=str handles dates
    }

