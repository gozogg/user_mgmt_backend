from alerts.alert_overdue import collect_job_alerts


def test_collect_job_alerts_splits_complete_and_not_complete():
    overdue, not_complete = collect_job_alerts(
        [
            {
                "status": "complete",
                "description": "Mow",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "date": "2026-03-01",
            },
            {
                "status": "not_complete",
                "description": "Trim",
                "first_name": "Alan",
                "last_name": "Turing",
                "date": "2026-03-02",
            },
            {
                "status": "invoiced",
                "description": "Ignore me",
                "first_name": "Grace",
                "last_name": "Hopper",
                "date": "2026-03-03",
            },
        ]
    )

    assert overdue == [
        {"description": "Mow", "name": "Ada Lovelace", "date": "2026-03-01"}
    ]
    assert not_complete == [
        {"description": "Trim", "name": "Alan Turing", "date": "2026-03-02"}
    ]
