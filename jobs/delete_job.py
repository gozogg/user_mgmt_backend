import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute
from org import require_organization
from response import json_response


def lambda_handler(event, context):
    """
    DELETE /jobs/{id}
    """
    job_id = event.get("pathParameters", {}).get("id")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    org_id, err = require_organization(event)
    if err:
        return err

    execute(
        "DELETE FROM jobs WHERE id = %s AND organization_id = %s",
        (job_id, org_id),
    )

    return json_response(204)
