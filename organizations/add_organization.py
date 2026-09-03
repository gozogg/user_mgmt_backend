import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning
from org import require_client_role
from response import json_response


def lambda_handler(event, context):
    """
    POST /organizations
    Body: { "business_name", "default_start_date", "default_end_date, alert_days, 'alert_email" }
    """
    forbidden = require_client_role(event)
    if forbidden:
        return forbidden

    body = json.loads(event.get("body") or "{}")

    business_name = body.get("business_name")
    default_start_date = body.get("default_start_date") or None
    default_end_date = body.get("default_end_date") or None
    alert_days = body.get("alert_days") or None
    alert_email = body.get("alert_email") or None

    if not business_name or not str(business_name).strip():
        return json_response(400, {"error": "business_name is required"})

    new_row = execute_returning(
        """
        INSERT INTO organizations (business_name, default_start_date, default_end_date, alert_days, alert_email)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (business_name.strip(), default_start_date, default_end_date, alert_days, alert_email),
    )

    return json_response(201, new_row)
