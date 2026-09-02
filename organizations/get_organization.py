import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    GET /organizations/{id}
    GET /organizations/me

    Organization is taken from the JWT. Path id must be "me" or the caller's org.
    """
    org_id, err = require_organization(event)
    if err:
        return err

    path_id = (event.get("pathParameters") or {}).get("id")
    if path_id and path_id != "me":
        try:
            if int(path_id) != org_id:
                return json_response(403, {"error": "forbidden"})
        except (TypeError, ValueError):
            return json_response(400, {"error": "id must be an integer or 'me'"})

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
