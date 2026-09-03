import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all, run_in_transaction, execute
from response import json_response
from send_alert_email_overdue import send_alert_email_overdue
from send_alert_email_not_complete import send_alert_email_not_complete

def lambda_handler(event, context):
    """
    EMAIL SCRIPT TO SEND ALERTS TO THE CLIENTS WHEN JOB_DATES ISN'T INVOICED
    """

    todays_date = datetime.now().date()
    organizations = fetch_all("SELECT id, alert_days, alert_email FROM organizations")

    for org in organizations:
        org_id = org['id']
        alert_days = org['alert_days']
        alert_email = org['alert_email']

        alert_date = todays_date - timedelta(days=alert_days)
        overdue = []
        not_complete = []

        rows = fetch_all("""
            SELECT 
                jd.*,
                j.description,
                c.first_name,
                c.last_name
            FROM job_dates as jd
            JOIN jobs j ON j.id = jd.job_id
            JOIN clients c ON c.id = j.client_id
            WHERE jd.organization_id = %s AND jd.status IN ('complete', 'not_complete') AND jd.date < %s
        """, (org_id, alert_date))

        for row in rows:
            if row['status'] == 'complete':
                overdue.append({
                    'description': row['description'],
                    'name': f"{row['first_name']} {row['last_name']}",
                    'date': row['date'],
                })
            elif row['status'] == 'not_complete':
                not_complete.append({
                    'description': row['description'],
                    'name': f"{row['first_name']} {row['last_name']}",
                    'date': row['date'],
                })
        
        if overdue:
            send_alert_email_overdue(alert_email, alert_days, overdue)
        if not_complete:
            send_alert_email_not_complete(alert_email, alert_days, not_complete)   

    return json_response(200, {"message": "Alerts sent successfully"})

if __name__ == "__main__":
    print(lambda_handler({}, None))
