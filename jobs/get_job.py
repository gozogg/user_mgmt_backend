import json
import sys
import os
from db import fetch_all
from response import json_response

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    GET /jobs?client_id
    """
    query_params = event.get("queryStringParameters") or {}
    client_id = query_params.get("client_id")

    if client_id:
        rows = fetch_all(
            "SELECT * FROM jobs WHERE client_id = %s ORDER BY start_date DESC",
            (client_id,),
        )
    else:
        rows = fetch_all("SELECT * FROM jobs ORDER BY start_date DESC")

    return json_response(200, rows)

