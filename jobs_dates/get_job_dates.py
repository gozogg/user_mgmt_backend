import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all


def lambda_handler(event, context):
    """
    GET /job-dates?date=YYYY-MM-DD
    GET /job-dates?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    GET /job-dates?client_id=2
    Filters can be combined, e.g. /job-dates?client_id=2&date=2026-08-17
    """
    query_params = event.get("queryStringParameters") or {}
    date = query_params.get("date")
    start_date = query_params.get("start_date")
    end_date = query_params.get("end_date")
    client_id = query_params.get("client_id")

    if (start_date and not end_date) or (end_date and not start_date):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "start_date and end_date must be provided together",
            }),
        }

    filters = []
    params = []

    if date:
        filters.append("jd.date = %s")
        params.append(date)
    elif start_date and end_date:
        filters.append("jd.date BETWEEN %s AND %s")
        params.extend([start_date, end_date])

    if client_id:
        filters.append("j.client_id = %s")
        params.append(client_id)

    if not filters:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "provide date, start_date and end_date, and/or client_id",
            }),
        }

    query = """
        SELECT
            jd.date,
            jd.status,
            j.id AS job_id,
            j.frequency,
            j.description,
            j.day_of_week,
            j.price,
            j.start_date,
            j.end_date,
            c.id AS client_id,
            c.first_name,
            c.last_name,
            c.address,
            c.phone_number,
            c.email
        FROM job_dates jd
        JOIN jobs j ON j.id = jd.job_id
        JOIN clients c ON c.id = j.client_id
        WHERE """ + " AND ".join(filters) + """
        ORDER BY jd.date, c.last_name, c.first_name
    """

    rows = fetch_all(query, tuple(params))

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(rows, default=str),
    }


if __name__ == "__main__":
    fake_event = {"queryStringParameters": {"client_id": "2"}}
    result = lambda_handler(fake_event, None)
    print(result)
