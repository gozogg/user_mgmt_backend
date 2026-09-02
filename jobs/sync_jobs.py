import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import fetch_all, run_in_transaction, execute
from response import json_response



def lambda_handler(event, context):
    """
    RUNS TO UPDATE JOB STATUSES
    COMPLETED: WHEN ALL JOB DATES ARE MARKED AS INVOICED
    FUTURE: WHEN THE JOB IS IN THE FUTURE
    CANCELLED: WHEN THE JOB IS CANCELLED
    ACTIVE: WHEN THE JOB IS ACTIVE AND ONGOING
    PAST DUE: WHEN THE JOB IS PAST THE END DATE AND NOT INVOICED
    """

    todays_date = datetime.now().date()
    organizations = fetch_all("SELECT id FROM organizations")

    for org in organizations:
        org_id = org['id']

        rows = fetch_all("""
            SELECT * FROM jobs
            WHERE organization_id = %s AND status IN ('active', 'future', 'past_due')
        """, (org_id,))

        for row in rows:
            job_id = row['id']
            start_date = row['start_date']
            end_date = row['end_date']
            print(f"Job ID: {job_id}, Start Date: {start_date}, End Date: {end_date}")
            print(f"Todays Date: {todays_date}")

            # always will be within the active region even for one time uses
            # active -> active; future -> active
            if todays_date <= end_date and todays_date >= start_date:
                status = 'active'
            # always will be future if it hasn't even hit the start date yet
            # future -> future;
            elif todays_date < start_date:
                status = 'future'
            # need to determine if it's past due or completed
            elif todays_date > end_date:
                not_invoiced = fetch_all("""
                    SELECT * FROM job_dates
                    WHERE organization_id = %s AND job_id = %s AND status NOT IN ('invoiced')
                """, (org_id, job_id,))
                if not not_invoiced:
                    status = 'completed'
                else:
                    status = 'past_due'
            print(f"Status: {status}")

            if status != row['status']:
                execute("""
                    UPDATE jobs SET status = %s WHERE id = %s AND organization_id = %s
                """, (status, job_id, org_id))
                print(f"Updated Job ID: {job_id}, Status: {status}")

    return json_response(200, {"message": "Jobs updated successfully"})

if __name__ == "__main__":
    print(lambda_handler({}, None))
