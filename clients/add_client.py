import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning
from response import json_response

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")

    address = body.get("address")
    city = body.get("city")
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    phone_number = body.get("phone_number")
    email = body.get("email")

    if not first_name:
        return json_response(400, {"error": "first name is required"})

    existing_client = execute_returning(
        "SELECT * FROM clients WHERE first_name = %s AND last_name = %s",
        (first_name, last_name,),
    )

    if existing_client:
        return json_response(400, {"error": "client with same first and last name exists"})
    
    new_row = execute_returning(
        """
        INSERT INTO clients (address, first_name, last_name, phone_number, email, city)
        VALUES(%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            address,
            first_name,
            last_name,
            phone_number,
            email,
            city
        ),
    )

    return json_response(201, new_row)