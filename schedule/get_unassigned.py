import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    GET /schedule/unassigned?organization_id=1
    """
    org_id, err = require_organization(event)
    if err:
        return err

    today = date.today()

    rows = fetch_all(
        """
        SELECT
            j.id,
            j.client_id,
            j.frequency,
            j.description,
            j.day_of_week,
            j.price,
            j.start_date,
            j.end_date,
            c.first_name,
            c.last_name,
            c.address,
            c.latitude,
            c.longitude
        FROM jobs j
        JOIN clients c ON c.id = j.client_id
        WHERE j.organization_id = %s
          AND j.frequency IN ('weekly', 'biweekly')
          AND j.day_of_week IS NULL
          AND (j.end_date IS NULL OR j.end_date >= %s)
        ORDER BY c.last_name, c.first_name
        """,
        (org_id, today),
    )

    return json_response(200, rows)
