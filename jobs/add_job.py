import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, fetch_all

def lambda_handler(event, context):
    body = json.loads(event.get("body" or "{}"))

    client_id = body.get("client_id")

    if not client_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "client_id is required"})
        }

    existing_client = fetch_all(
        "SELECT id FROM clients WHERE id = %s",
        (client_id,),
    )
    if not existing_client:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"client with id {client_id} not found"})
        }

    new_row = execute_returning(
        """
        INSERT INTO jobs (client_id, frequency, description, day_of_week, price)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            body.get('client_id'),
            body.get('frequency'),
            body.get('description'),
            body.get('day_of_week'),
            body.get('price')
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
            "client_id": 2,
            "frequency": 'weekly',
            "description": "cutting grass",
            "day_of_week": "Monday",
            "price": 20,
        })
    }
    result = lambda_handler(fake_event, None)
    print(result)