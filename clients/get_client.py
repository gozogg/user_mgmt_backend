import json
import sys
import os

# Lets this file import db.py from the parent folder when run locally.
# When deployed as a real Lambda, you'll package db.py alongside this
# file (or use a Lambda layer) instead of relying on this path trick.
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from response import json_response


def lambda_handler(event, context):
    """
    GET /clients
    GET /clients?city
    GET /clients?client_id
    """
    query_params = event.get("queryStringParameters") or {}
    city = query_params.get("city")
    client_id = query_params.get("client_id")

    if city:
        rows = fetch_all(
            "SELECT * FROM clients WHERE city = %s ORDER BY last_name ASC",
            (city,),
        )
    elif client_id:
        rows = fetch_all(
            "SELECT * FROM clients WHERE id = %s ORDER BY last_name ASC",
            (client_id,),
        )
    else:
        rows = fetch_all("SELECT * FROM clients ORDER BY last_name ASC")

    return json_response(200, rows)


if __name__ == "__main__":
    fake_event = {"queryStringParameters": None}
    result = lambda_handler(fake_event, None)
    print(result)
