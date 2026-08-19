import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all, run_in_transaction
from jobs.generate_dates import VALID_FREQUENCIES, generate_occurrence_dates
from response import json_response


def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")

    client_id = body.get("client_id")
    frequency = body.get("frequency")
    description = body.get("description")
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    day_of_week = body.get("day_of_week")
    price = body.get("price")

    if not client_id:
        return json_response(400, {"error": "client_id is required"})

    if frequency not in VALID_FREQUENCIES:
        return json_response(400, {
            "error": "frequency must be weekly, biweekly, or onetime",
        })

    if not description:
        return json_response(400, {"error": "description is required"})

    if not start_date:
        return json_response(400, {"error": "start_date is required"})

    if frequency != "onetime" and not end_date:
        return json_response(400, {
            "error": "end_date is required for weekly and biweekly jobs",
        })

    existing_client = fetch_all(
        "SELECT id FROM clients WHERE id = %s",
        (client_id,),
    )
    if not existing_client:
        return json_response(404, {"error": f"client with id {client_id} not found"})

    try:
        occurrence_dates = generate_occurrence_dates(
            frequency,
            start_date,
            end_date=end_date,
            day_of_week=day_of_week,
        )
    except ValueError as e:
        return json_response(400, {"error": str(e)})

    if not occurrence_dates:
        return json_response(400, {
            "error": "no occurrences fall between start_date and end_date",
        })

    def create_job_and_dates(cur):
        cur.execute(
            """
            INSERT INTO jobs (
                client_id, frequency, description, day_of_week,
                price, start_date, end_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                client_id,
                frequency,
                description,
                day_of_week,
                price,
                start_date,
                end_date,
            ),
        )
        job = dict(cur.fetchone())
        cur.executemany(
            "INSERT INTO job_dates (job_id, date) VALUES (%s, %s)",
            [(job["id"], d) for d in occurrence_dates],
        )
        job["dates"] = [str(d) for d in occurrence_dates]
        return job

    new_row = run_in_transaction(create_job_and_dates)

    return json_response(201, new_row)

