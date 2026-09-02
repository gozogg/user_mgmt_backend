import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all, run_in_transaction
from jobs.generate_dates import VALID_FREQUENCIES, generate_occurrence_dates
from org import require_organization
from response import json_response

SCHEDULE_FIELDS = {"frequency", "day_of_week", "start_date", "end_date"}
VALID_JOB_STATUSES = {"active", "completed", "future", "cancelled", "past_due"}


def _update_job_row(cur, updates, job_id, org_id):
    set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
    values = list(updates.values()) + [job_id, org_id]
    cur.execute(
        f"UPDATE jobs SET {set_clause} WHERE id = %s AND organization_id = %s RETURNING *",
        values,
    )
    row = cur.fetchone()
    return dict(row) if row else None


def _delete_incomplete_dates(cur, job_id, org_id):
    cur.execute(
        """
        DELETE FROM job_dates
        WHERE job_id = %s
          AND organization_id = %s
          AND status = 'not_complete'
        """,
        (job_id, org_id),
    )


def lambda_handler(event, context):
    """
    PUT /jobs/{id}
    """
    job_id = event.get("pathParameters", {}).get("id")
    body = json.loads(event.get("body") or "{}")

    if not job_id:
        return json_response(400, {"error": "id is required in the URL path"})

    org_id, err = require_organization(event, body)
    if err:
        return err

    allowed_fields = ["client_id", "frequency", "description", "day_of_week", "price", "start_date", "end_date", "status"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        return json_response(400, {"error": "no valid fields to update"})

    if "status" in updates and updates["status"] not in VALID_JOB_STATUSES:
        return json_response(400, {
            "error": "status must be active, completed, future, cancelled, or past_due",
        })

    existing_rows = fetch_all(
        "SELECT * FROM jobs WHERE id = %s AND organization_id = %s",
        (job_id, org_id),
    )
    if not existing_rows:
        return json_response(404, {"error": "job not found"})

    merged = {**existing_rows[0], **updates}

    if merged["frequency"] not in VALID_FREQUENCIES:
        return json_response(400, {
            "error": "frequency must be weekly, biweekly, or onetime",
        })

    if merged["frequency"] in ("weekly", "biweekly") and not merged.get("end_date"):
        return json_response(400, {
            "error": "end_date is required for weekly and biweekly jobs",
        })

    if "client_id" in updates:
        existing_client = fetch_all(
            "SELECT id FROM clients WHERE id = %s AND organization_id = %s",
            (updates["client_id"], org_id),
        )
        if not existing_client:
            return json_response(404, {"error": "client not found"})

    cancelling = merged.get("status") == "cancelled"
    regenerate_schedule = bool(SCHEDULE_FIELDS & updates.keys()) and not cancelling

    if regenerate_schedule:
        try:
            occurrence_dates = generate_occurrence_dates(
                merged["frequency"],
                merged["start_date"],
                end_date=merged.get("end_date"),
                day_of_week=merged.get("day_of_week"),
            )
        except ValueError as e:
            return json_response(400, {"error": str(e)})

        if not occurrence_dates:
            return json_response(400, {
                "error": "no occurrences fall between start_date and end_date",
            })

        def update_job_and_dates(cur):
            job = _update_job_row(cur, updates, job_id, org_id)
            if not job:
                return None

            cur.execute(
                """
                DELETE FROM job_dates
                WHERE job_id = %s AND organization_id = %s AND status = 'not_complete'
                """,
                (job_id, org_id),
            )
            cur.executemany(
                """
                INSERT INTO job_dates (job_id, organization_id, date)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_id, date) DO NOTHING
                """,
                [(job["id"], org_id, d) for d in occurrence_dates],
            )
            cur.execute(
                "SELECT date FROM job_dates WHERE job_id = %s ORDER BY date",
                (job["id"],),
            )
            job["dates"] = [str(row["date"]) for row in cur.fetchall()]
            return job

        updated_row = run_in_transaction(update_job_and_dates)
        if not updated_row:
            return json_response(404, {"error": "job not found"})

        return json_response(200, updated_row)

    def update_job(cur):
        job = _update_job_row(cur, updates, job_id, org_id)
        if not job:
            return None
        if cancelling:
            _delete_incomplete_dates(cur, job_id, org_id)
        return job

    updated_row = run_in_transaction(update_job)

    if not updated_row:
        return json_response(404, {"error": "job not found"})

    return json_response(200, updated_row)
