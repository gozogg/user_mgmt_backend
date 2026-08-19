import json
import sys
import os
from db import execute
from response import json_response

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    DELETE /jobs/{id}
    """
    job_id = event.get("pathParameters", {}).get("id")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    execute("DELETE FROM jobs WHERE id = %s", (job_id,))

    return json_response(204)
