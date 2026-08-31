import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning
from response import json_response


def lambda_handler(event, context):
    """
    POST /organizations
    Body: { "business_name", "default_start_date", "default_end_date" }
    """
    body = json.loads(event.get("body") or "{}")

    business_name = body.get("business_name")
    default_start_date = body.get("default_start_date") or None
    default_end_date = body.get("default_end_date") or None

    if not business_name or not str(business_name).strip():
        return json_response(400, {"error": "business_name is required"})

    new_row = execute_returning(
        """
        INSERT INTO organizations (business_name, default_start_date, default_end_date)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (business_name.strip(), default_start_date, default_end_date),
    )

    return json_response(201, new_row)
