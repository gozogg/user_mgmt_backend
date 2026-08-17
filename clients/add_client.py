import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning

def lambda_handler(event, context):
    body = json.loads(event.get("body" or "{}"))

    first_name = body.get("first_name")

    if not first_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error: ": "first name is required"})
        }
    
    new_row = execute_returning(
        """
        INSERT INTO clients (address, price_per_grass, first_name, last_name)
        VALUES(%s, %s, %s, %s)
        RETURNING *
        """,
        (
            body.get('address'),
            body.get('price_per_grass'),
            first_name,
            body.get('last_name')
        ),
    )

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "applications/json"},
        "body": json.dumps(new_row, default=str)
    }

if __name__ == "__main__":
    fake_event = {
        "body": json.dumps({
            "address": "31491 norfolk",
            "price_per_grass": 40,
            "first_name": "Tina",
            "last_name": "Pamboukdjian",
        })
    }
    result = lambda_handler(fake_event, None)
    print(result)