import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    GET /clients
    GET /clients?city
    GET /clients?client_id
    GET /clients?organization_id=1
    """
    query_params = event.get("queryStringParameters") or {}
    org_id, err = require_organization(event)
    if err:
        return err

    city = query_params.get("city")
    client_id = query_params.get("client_id")

    if city:
        rows = fetch_all(
            """
            SELECT * FROM clients
            WHERE organization_id = %s AND city = %s
            ORDER BY last_name ASC
            """,
            (org_id, city),
        )
    elif client_id:
        rows = fetch_all(
            """
            SELECT * FROM clients
            WHERE organization_id = %s AND id = %s
            ORDER BY last_name ASC
            """,
            (org_id, client_id),
        )
    else:
        rows = fetch_all(
            "SELECT * FROM clients WHERE organization_id = %s ORDER BY last_name ASC",
            (org_id,),
        )

    return json_response(200, rows)
