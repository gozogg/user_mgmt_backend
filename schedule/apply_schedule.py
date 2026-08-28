import json
import sys
import os
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import run_in_transaction
from response import json_response
from schedule.optimizer import apply_schedule, parse_date


def lambda_handler(event, context):
    """
    POST /schedule/apply
    Body: preview payload from /schedule/preview plus from_date/to_date.
    """
    body = json.loads(event.get("body") or "{}")
    today = date.today()

    preview = body.get("preview")
    if not preview:
        return json_response(400, {"error": "preview is required"})

    try:
        from_date = parse_date(body.get("from_date") or preview.get("from_date") or today)
        to_date = parse_date(
            body.get("to_date") or preview.get("to_date") or date(today.year, 12, 31)
        )
    except ValueError:
        return json_response(400, {"error": "from_date and to_date must be YYYY-MM-DD"})

    if to_date < from_date:
        return json_response(400, {"error": "to_date must be on or after from_date"})

    result = run_in_transaction(lambda cur: apply_schedule(preview, from_date, to_date, cur))
    return json_response(200, result)
