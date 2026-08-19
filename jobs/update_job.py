import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, run_in_transaction, fetch_all
from jobs.generate_dates import VALID_FREQUENCIES, generate_occurrence_dates

SCHEDULE_FIELDS = {"frequency", "day_of_week", "start_date", "end_date"}


def lambda_handler(event, context):
    """
    PUT /jobs/{id}
    """
    job_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "id is required in the URL path"})}

    allowed_fields = ["client_id", "frequency", "description", "day_of_week", "price", "start_date", "end_date"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return {"statusCode": 400, "body": json.dumps({"error": "no valid fields to update"})}

    existing_rows = fetch_all("SELECT * FROM jobs WHERE id = %s", (job_id,))
    if not existing_rows:
        return {"statusCode": 404, "body": json.dumps({"error": "job not found"})}

    merged = {**existing_rows[0], **updates}

    if merged["frequency"] not in VALID_FREQUENCIES:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "frequency must be weekly, biweekly, or onetime",
            }),
        }

    if merged["frequency"] in ("weekly", "biweekly") and not merged.get("end_date"):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "end_date is required for weekly and biweekly jobs",
            }),
        }

    if "client_id" in updates:
        existing_client = fetch_all(
            "SELECT id FROM clients WHERE id = %s",
            (updates["client_id"],),
        )
        if not existing_client:
            return {"statusCode": 404, "body": json.dumps({"error": "client not found"})}

    if SCHEDULE_FIELDS & updates.keys():
        try:
            occurrence_dates = generate_occurrence_dates(
                merged["frequency"],
                merged["start_date"],
                end_date=merged.get("end_date"),
                day_of_week=merged.get("day_of_week"),
            )
        except ValueError as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)}),
            }

        if not occurrence_dates:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "no occurrences fall between start_date and end_date",
                }),
            }

        def update_job_and_dates(cur):
            set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
            values = list(updates.values()) + [job_id]
            cur.execute(
                f"UPDATE jobs SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )
            job_row = cur.fetchone()
            if not job_row:
                return None

            job = dict(job_row)
            cur.execute(
                "DELETE FROM job_dates WHERE job_id = %s AND status = 'not_complete'",
                (job_id,),
            )
            cur.executemany(
                """
                INSERT INTO job_dates (job_id, date) VALUES (%s, %s)
                ON CONFLICT (job_id, date) DO NOTHING
                """,
                [(job["id"], d) for d in occurrence_dates],
            )
            cur.execute(
                "SELECT date FROM job_dates WHERE job_id = %s ORDER BY date",
                (job["id"],),
            )
            job["dates"] = [str(row["date"]) for row in cur.fetchall()]
            return job

        updated_row = run_in_transaction(update_job_and_dates)
        if not updated_row:
            return {"statusCode": 404, "body": json.dumps({"error": "job not found"})}

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(updated_row, default=str),
        }

    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [job_id]

    updated_row = execute_returning(
        f"UPDATE jobs SET {set_clause} WHERE id = %s RETURNING *",
        values,
    )

    if not updated_row:
        return {"statusCode": 404, "body": json.dumps({"error": "job not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(updated_row, default=str),
    }


if __name__ == "__main__":
    fake_event = {
        "pathParameters": {"id": "2"},
        "body": json.dumps({"description": "grass_cut"}),
    }
    result = lambda_handler(fake_event, None)
    print(result)
