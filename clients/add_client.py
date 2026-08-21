import json

from db import fetch_all, execute_returning
from response import json_response


def lambda_handler(event, context):
    try:
        raw_body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64
            raw_body = base64.b64decode(raw_body).decode("utf-8")
        if isinstance(raw_body, dict):
            body = raw_body
        else:
            body = json.loads(raw_body)

        address = body.get("address")
        city = body.get("city")
        first_name = body.get("first_name")
        last_name = body.get("last_name")
        phone_number = body.get("phone_number")
        email = body.get("email")

        if not first_name:
            return json_response(400, {"error": "first name is required"})

        existing_clients = fetch_all(
            "SELECT id FROM clients WHERE first_name = %s AND last_name = %s",
            (first_name, last_name),
        )

        if existing_clients:
            return json_response(400, {"error": "client with same first and last name exists"})

        new_row = execute_returning(
            """
            INSERT INTO clients (address, first_name, last_name, phone_number, email, city)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                address,
                first_name,
                last_name,
                phone_number,
                email,
                city,
            ),
        )

        return json_response(201, new_row)
    except Exception as e:
        # Surface the real error in the response so the browser Network tab
        # shows it instead of a generic API Gateway 500.
        return json_response(500, {"error": str(e)})
