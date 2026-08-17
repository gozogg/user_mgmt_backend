import json
import sys
import os

# Lets this file import db.py from the parent folder when run locally.
# When deployed as a real Lambda, you'll package db.py alongside this
# file (or use a Lambda layer) instead of relying on this path trick.
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all


def lambda_handler(event, context):
    """
    GET /clients
    """
    query_params = event.get("queryStringParameters") or {}
    # status_filter = query_params.get("status")

    # if status_filter:
    #     rows = fetch_all(
    #         "SELECT * FROM applications WHERE status = %s ORDER BY date_applied DESC",
    #         (status_filter,),
    #     )
    # else:
    rows = fetch_all("SELECT * FROM clients")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(rows, default=str),  # default=str handles dates
    }


if __name__ == "__main__":
    fake_event = {"queryStringParameters": None}
    result = lambda_handler(fake_event, None)
    print(result)
