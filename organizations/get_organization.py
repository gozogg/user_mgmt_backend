import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from response import json_response


def lambda_handler(event, context):
    """
    GET /organizations/{id}
    """
    org_id = event.get("pathParameters", {}).get("id")

    if not org_id:
        return json_response(400, {"error": "id is required in the URL path"})

    rows = fetch_all(
        """
        SELECT id, business_name, default_start_date, default_end_date, alert_days, alert_email
        FROM organizations
        WHERE id = %s
        """,
        (org_id,),
    )

    if not rows:
        return json_response(404, {"error": "organization not found"})

    return json_response(200, rows[0])
