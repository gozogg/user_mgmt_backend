import json
import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from response import json_response
from schedule.optimizer import build_schedule_preview, parse_date


JOBS_SELECT = """
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
    WHERE j.frequency IN ('weekly', 'biweekly')
      AND (j.end_date IS NULL OR j.end_date >= %s)
"""


def lambda_handler(event, context):
    """
    POST /schedule/preview
    Body: { "from_date": "YYYY-MM-DD", "to_date": "YYYY-MM-DD" }
    """
    body = json.loads(event.get("body") or "{}")
    today = date.today()

    try:
        from_date = parse_date(body.get("from_date") or today)
        to_date = parse_date(body.get("to_date") or date(today.year, 12, 31))
    except ValueError:
        return json_response(400, {"error": "from_date and to_date must be YYYY-MM-DD"})

    if to_date < from_date:
        return json_response(400, {"error": "to_date must be on or after from_date"})

    all_jobs = fetch_all(JOBS_SELECT, (today,))
    unassigned_jobs = [j for j in all_jobs if not j.get("day_of_week")]

    preview = build_schedule_preview(all_jobs, unassigned_jobs, from_date, to_date)
    return json_response(200, preview)
