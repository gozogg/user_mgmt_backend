import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from org import require_organization
from response import json_response

JOBS_SELECT = """
    SELECT
        j.*,
        c.first_name,
        c.last_name,
        c.address,
        c.city,
        c.latitude,
        c.longitude
    FROM jobs j
    JOIN clients c ON c.id = j.client_id
"""


def _as_list(value):
    if not value:
        return []
    if isinstance(value, list):
        items = []
        for v in value:
            items.extend(
                part.strip()
                for part in str(v).split(",")
                if part.strip()
            )
        return items
    return [v.strip() for v in value.split(",") if v.strip()]


def lambda_handler(event, context):
    """
    GET /jobs?organization_id=1
    """
    query_params = event.get("queryStringParameters") or {}
    multi_params = event.get("multiValueQueryStringParameters") or {}

    org_id, err = require_organization(event)
    if err:
        return err

    client_id = query_params.get("client_id")
    job_id = query_params.get("job_id")
    frequencies = _as_list(
        multi_params.get("frequency") or query_params.get("frequency")
    )
    days = _as_list(
        multi_params.get("day_of_week") or query_params.get("day_of_week")
    )

    if job_id:
        rows = fetch_all(
            JOBS_SELECT + " WHERE j.id = %s AND j.organization_id = %s",
            (job_id, org_id),
        )
        return json_response(200, rows)

    filters = ["j.organization_id = %s"]
    params = [org_id]

    if client_id:
        filters.append("j.client_id = %s")
        params.append(client_id)

    if frequencies:
        placeholders = ", ".join(["%s"] * len(frequencies))
        filters.append(f"j.frequency IN ({placeholders})")
        params.extend(frequencies)

    if days:
        placeholders = ", ".join(["%s"] * len(days))
        filters.append(f"j.day_of_week IN ({placeholders})")
        params.extend(days)

    where = " WHERE " + " AND ".join(filters)
    rows = fetch_all(
        JOBS_SELECT + where + " ORDER BY j.start_date DESC",
        tuple(params),
    )
    return json_response(200, rows)
