import json
import sys
import os
from datetime import datetime, timedelta
import resend
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all, run_in_transaction, execute
from response import json_response

def send_alert_email_not_complete(alert_email, alert_days, not_complete):
    """
    SEND ALERTS TO THE CLIENTS WHEN JOB_DATES ISN'T INVOICED
    """

    if not_complete:
        html = f"<p>You have the following jobs that have not been marked completed at least {alert_days} days ago. Either mark the jobs completed or delete them in the app:</p><ul>"
        num_not_complete = len(not_complete)
        for x in not_complete:
            html += f"<li>{x['name']} - {x['date']} - {x['description']}</li>"
        html += "</ul>"
        subject = f"You have {num_not_complete} not complete jobs"
        try:
            params: resend.Emails.SendParams = {
                "from": "onboarding@resend.dev",
                "to": [alert_email],
                "subject": subject,
                "html": html,
            }
            email: resend.Emails.SendResponse = resend.Emails.send(params)
            return json_response(200, {f"message": email})
        except Exception as e:
            print(e)
            return json_response(500, {"message": f"Failed to send alert email: {e}"})
    

