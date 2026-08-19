import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")

    address = body.get("address")
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    phone_number = body.get("phone_number")
    email = body.get("email")

    if not first_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error: ": "first name is required"})
        }
    
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

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "applications/json"},
        "body": json.dumps(new_row, default=str)
    }