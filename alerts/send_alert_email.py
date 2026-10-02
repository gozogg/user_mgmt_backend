import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from alerts.send_alerts import (
    send_alert_email_not_complete,
    send_alert_email_overdue,
)


def lambda_handler(event, context):
    """
    SQS consumer that lives outside the VPC and talks to Resend.
    """
    if not os.getenv("RESEND_API_KEY"):
        raise RuntimeError("RESEND_API_KEY is not set")

    for record in event.get("Records") or []:
        payload = json.loads(record["body"])
        kind = payload.get("type")
        alert_email = payload.get("alert_email")
        alert_days = payload.get("alert_days")
        jobs = payload.get("jobs") or []

        if kind == "overdue":
            send_alert_email_overdue(alert_email, alert_days, jobs)
        elif kind == "not_complete":
            send_alert_email_not_complete(alert_email, alert_days, jobs)
        else:
            raise ValueError(f"unknown alert type: {kind}")

    return {"ok": True}
