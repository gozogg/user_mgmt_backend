import json
import os
import sys
from datetime import datetime, timedelta

import boto3

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all
from response import json_response

sqs = boto3.client("sqs")


def collect_job_alerts(rows):
    overdue = []
    not_complete = []
    for row in rows:
        item = {
            "description": row["description"],
            "name": f"{row['first_name']} {row['last_name']}",
            "date": str(row["date"]),
        }
        if row["status"] == "complete":
            overdue.append(item)
        elif row["status"] == "not_complete":
            not_complete.append(item)
    return overdue, not_complete


def enqueue_alert(payload):
    queue_url = os.environ.get("ALERT_QUEUE_URL")
    if not queue_url:
        raise RuntimeError("ALERT_QUEUE_URL is not set")
    sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))


def lambda_handler(event, context):
    """
    Look up overdue / not-complete job dates in RDS, then hand email off to
    an out-of-VPC Lambda via SQS so Resend does not need a NAT Gateway.
    """
    todays_date = datetime.now().date()
    organizations = fetch_all(
        "SELECT id, alert_days, alert_email FROM organizations"
    )
    queued = 0

    for org in organizations:
        org_id = org["id"]
        alert_days = org["alert_days"]
        alert_email = org["alert_email"]
        if not alert_email or alert_days is None:
            continue

        alert_date = todays_date - timedelta(days=alert_days)
        rows = fetch_all(
            """
            SELECT
                jd.*,
                j.description,
                c.first_name,
                c.last_name
            FROM job_dates as jd
            JOIN jobs j ON j.id = jd.job_id
            JOIN clients c ON c.id = j.client_id
            WHERE jd.organization_id = %s
              AND jd.status IN ('complete', 'not_complete')
              AND jd.date < %s
            """,
            (org_id, alert_date),
        )
        overdue, not_complete = collect_job_alerts(rows)

        if overdue:
            enqueue_alert(
                {
                    "type": "overdue",
                    "alert_email": alert_email,
                    "alert_days": alert_days,
                    "jobs": overdue,
                }
            )
            queued += 1
        if not_complete:
            enqueue_alert(
                {
                    "type": "not_complete",
                    "alert_email": alert_email,
                    "alert_days": alert_days,
                    "jobs": not_complete,
                }
            )
            queued += 1

    return json_response(200, {"message": "Alerts queued successfully", "queued": queued})
