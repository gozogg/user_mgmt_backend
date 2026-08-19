import json
import sys
import os
from db import execute

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

def lambda_handler(event, context):
    """
    DELETE /job-dates/{id}/{date}
    """
    job_id = event.get("pathParameters", {}).get("id")
    date = event.get("pathParameters", {}).get("date")

    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id is required in the URL path"})}

    if not date:
        return {"statusCode": 400, "body": json.dumps({"error": "date is required in the URL path"})}

    execute("DELETE FROM job_dates WHERE job_id = %s AND date = %s", (job_id, date,))

    return {
        "statusCode": 204,
        "body": "",
    }