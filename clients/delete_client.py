import json
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute
from response import json_response


def lambda_handler(event, context):
    """
    DELETE /clients/{id}
    """
    client_id = event.get("pathParameters", {}).get("id")

    if not client_id:
        return json_response(400, {"error": "id is required in the URL path"})

    execute("DELETE FROM clients WHERE id = %s", (client_id,))

    return json_response(204)
