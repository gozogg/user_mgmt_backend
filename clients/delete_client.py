import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute


def lambda_handler(event, context):
    """
    DELETE /applications/{id}
    """
    client_id = event.get("pathParameters", {}).get("id")

    if not client_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id is required in the URL path"})}

    execute("DELETE FROM clients WHERE id = %s", (client_id,))

    return {
        "statusCode": 204,
        "body": "",
    }


if __name__ == "__main__":
    fake_event = {"pathParameters": {"id": "1"}}
    result = lambda_handler(fake_event, None)
    print(result)