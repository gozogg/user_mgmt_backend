from schedule.optimizer import (
    build_schedule_preview,
    optimize_route,
    route_distance_miles,
    suggest_day_of_week,
)

DEPOT = (42.0, -83.0)


def _job(job_id, lat=None, lon=None, **extra):
    job = {
        "id": job_id,
        "client_id": job_id,
        "first_name": "Pat",
        "last_name": f"Client{job_id}",
        "description": f"Job {job_id}",
        "frequency": "weekly",
        "day_of_week": extra.pop("day_of_week", None),
        "latitude": lat,
        "longitude": lon,
    }
    job.update(extra)
    return job


def test_optimize_route_visits_nearest_stop_first():
    near = _job(1, 42.01, -83.01)
    far = _job(2, 43.00, -84.00)
    ordered = optimize_route([far, near], depot=DEPOT)
    assert [job["id"] for job in ordered] == [1, 2]


def test_optimize_route_appends_jobs_without_coordinates():
    with_coords = _job(1, 42.01, -83.01)
    missing = _job(2)
    ordered = optimize_route([missing, with_coords], depot=DEPOT)
    assert [job["id"] for job in ordered] == [1, 2]


def test_route_distance_is_zero_without_coordinates():
    assert route_distance_miles([_job(1)], depot=DEPOT) == 0.0


def test_suggest_day_picks_closest_existing_route():
    monday_job = _job(10, 42.01, -83.01, day_of_week="monday")
    friday_job = _job(11, 44.00, -85.00, day_of_week="friday")
    unassigned = _job(12, 42.02, -83.02)

    day, miles = suggest_day_of_week(
        unassigned,
        {"monday": [monday_job], "friday": [friday_job]},
    )
    assert day == "monday"
    assert miles is not None
    assert miles < 10


def test_suggest_day_falls_back_to_lightest_day_when_no_coords_on_routes():
    unassigned = _job(12, 42.02, -83.02)
    day, miles = suggest_day_of_week(
        unassigned,
        {"monday": [_job(1)], "tuesday": []},
    )
    assert day == "tuesday"
    assert miles is None


def test_preview_assigns_weekly_jobs_and_skips_onetime():
    existing = _job(1, 42.01, -83.01, day_of_week="monday")
    weekly = _job(2, 42.02, -83.02, frequency="weekly")
    onetime = _job(3, 42.03, -83.03, frequency="onetime")

    preview = build_schedule_preview(
        [existing],
        [weekly, onetime],
        "2026-03-01",
        "2026-03-31",
    )

    assert preview["unassigned_count"] == 2
    assert len(preview["assignments"]) == 1
    assert preview["assignments"][0]["job_id"] == 2
    assert preview["assignments"][0]["suggested_day_of_week"] == "monday"
    assert preview["routes"]["monday"]["stop_count"] == 2
    assert preview["routes"]["monday"]["stops"][0]["stop_order"] == 1
