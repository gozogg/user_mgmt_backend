import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning
from response import json_response

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")

    address = body.get("address")
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    phone_number = body.get("phone_number")
    email = body.get("email")

    if not first_name:
        return json_response(400, {"error": "first name is required"})
    
    new_row = execute_returning(
        """
        INSERT INTO clients (address, first_name, last_name, phone_number, email)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            address,
            first_name,
            last_name,
            phone_number,
            email
        ),
    )

    return json_response(201, new_row)