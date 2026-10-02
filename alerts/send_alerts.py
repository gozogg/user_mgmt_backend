import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def _job_list_html(jobs):
    items = "".join(
        f"<li>{job['name']} - {job['date']} - {job['description']}</li>"
        for job in jobs
    )
    return f"<ul>{items}</ul>"


def send_alert_email_overdue(alert_email, alert_days, overdue):
    if not alert_email or not overdue:
        return None

    html = (
        f"<p>You have the following jobs that have been completed at least "
        f"{alert_days} days ago:</p>{_job_list_html(overdue)}"
    )
    return resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": [alert_email],
            "subject": f"You have {len(overdue)} overdue jobs",
            "html": html,
        }
    )


def send_alert_email_not_complete(alert_email, alert_days, not_complete):
    if not alert_email or not not_complete:
        return None

    html = (
        f"<p>You have the following jobs that have not been marked completed "
        f"at least {alert_days} days ago. Either mark the jobs completed or "
        f"delete them in the app:</p>{_job_list_html(not_complete)}"
    )
    return resend.Emails.send(
        {
            "from": "onboarding@resend.dev",
            "to": [alert_email],
            "subject": f"You have {len(not_complete)} not complete jobs",
            "html": html,
        }
    )
