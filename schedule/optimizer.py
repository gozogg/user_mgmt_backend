import math
from datetime import date, datetime

from jobs.generate_dates import generate_occurrence_dates

DEFAULT_DEPOT = (42.43716, -83.35697)  # lat, lon
WEEKDAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_date(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def haversine_miles(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


def _coords(job):
    lat = job.get("latitude")
    lon = job.get("longitude")
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def route_distance_miles(jobs, depot=DEFAULT_DEPOT):
    points = [_coords(job) for job in jobs]
    points = [p for p in points if p]
    if not points:
        return 0.0

    total = 0.0
    cur_lat, cur_lon = depot
    for lat, lon in points:
        total += haversine_miles(cur_lat, cur_lon, lat, lon)
        cur_lat, cur_lon = lat, lon
    return round(total, 1)


def optimize_route(jobs, depot=DEFAULT_DEPOT):
    """Nearest-neighbor route. Jobs without coordinates are appended at the end."""
    depot_lat, depot_lon = depot
    valid = [j for j in jobs if _coords(j)]
    invalid = [j for j in jobs if not _coords(j)]

    remaining = valid[:]
    ordered = []
    cur_lat, cur_lon = depot_lat, depot_lon

    while remaining:
        nearest = min(
            remaining,
            key=lambda j: haversine_miles(cur_lat, cur_lon, *_coords(j)),
        )
        ordered.append(nearest)
        remaining.remove(nearest)
        cur_lat, cur_lon = _coords(nearest)

    ordered.extend(invalid)
    return ordered


def suggest_day_of_week(unassigned_job, day_jobs):
    """Pick the weekday whose existing route is closest to this job."""
    coords = _coords(unassigned_job)
    if not coords:
        for day in WEEKDAY_ORDER:
            if day in day_jobs:
                return day, None
        return "monday", None

    job_lat, job_lon = coords
    best_day = None
    best_dist = float("inf")

    for day in WEEKDAY_ORDER:
        jobs = day_jobs.get(day, [])
        if not jobs:
            continue
        for existing in jobs:
            existing_coords = _coords(existing)
            if not existing_coords:
                continue
            dist = haversine_miles(job_lat, job_lon, *existing_coords)
            if dist < best_dist:
                best_dist = dist
                best_day = day

    if best_day:
        return best_day, round(best_dist, 1)

    lightest = min(WEEKDAY_ORDER, key=lambda d: len(day_jobs.get(d, [])))
    return lightest, None


def _job_summary(job, stop_order=None):
    return {
        "job_id": job["id"],
        "client_id": job["client_id"],
        "first_name": job.get("first_name"),
        "last_name": job.get("last_name"),
        "description": job.get("description"),
        "frequency": job.get("frequency"),
        "day_of_week": job.get("day_of_week"),
        "latitude": job.get("latitude"),
        "longitude": job.get("longitude"),
        "stop_order": stop_order,
    }


def build_schedule_preview(all_jobs, unassigned_jobs, from_date, to_date):
    day_jobs = {day: [] for day in WEEKDAY_ORDER}

    for job in all_jobs:
        day = (job.get("day_of_week") or "").strip().lower()
        if day in day_jobs:
            day_jobs[day].append(dict(job))

    assignments = []
    working_unassigned = [dict(j) for j in unassigned_jobs]

    for job in working_unassigned:
        if job.get("frequency") not in ("weekly", "biweekly"):
            continue
        suggested_day, nearest_miles = suggest_day_of_week(job, day_jobs)
        job["day_of_week"] = suggested_day
        day_jobs[suggested_day].append(job)
        assignments.append({
            "job_id": job["id"],
            "first_name": job.get("first_name"),
            "last_name": job.get("last_name"),
            "description": job.get("description"),
            "frequency": job.get("frequency"),
            "suggested_day_of_week": suggested_day,
            "nearest_miles": nearest_miles,
        })

    routes = {}
    for day in WEEKDAY_ORDER:
        jobs = day_jobs.get(day, [])
        if not jobs:
            routes[day] = {
                "stop_count": 0,
                "estimated_miles": 0,
                "stops": [],
            }
            continue

        ordered = optimize_route(jobs)
        stops = [
            _job_summary(job, stop_order=i + 1)
            for i, job in enumerate(ordered)
        ]
        routes[day] = {
            "stop_count": len(stops),
            "estimated_miles": route_distance_miles(ordered),
            "stops": stops,
        }

    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "unassigned_count": len(working_unassigned),
        "assignments": assignments,
        "routes": routes,
    }


def apply_schedule(preview, from_date, to_date, organization_id, cur):
    assignments = preview.get("assignments") or []
    routes = preview.get("routes") or {}

    assigned_job_ids = set()
    for item in assignments:
        job_id = item["job_id"]
        day_of_week = item["suggested_day_of_week"]
        assigned_job_ids.add(job_id)

        cur.execute(
            "SELECT * FROM jobs WHERE id = %s AND organization_id = %s",
            (job_id, organization_id),
        )
        job_row = cur.fetchone()
        if not job_row:
            continue

        job = dict(job_row)
        cur.execute(
            "UPDATE jobs SET day_of_week = %s WHERE id = %s AND organization_id = %s",
            (day_of_week, job_id, organization_id),
        )

        occurrence_dates = generate_occurrence_dates(
            job["frequency"],
            job["start_date"],
            end_date=job.get("end_date"),
            day_of_week=day_of_week,
        )
        cur.execute(
            """
            DELETE FROM job_dates
            WHERE job_id = %s AND organization_id = %s AND status = 'not_complete'
            """,
            (job_id, organization_id),
        )
        cur.executemany(
            """
            INSERT INTO job_dates (job_id, organization_id, date)
            VALUES (%s, %s, %s)
            ON CONFLICT (job_id, date) DO NOTHING
            """,
            [(job_id, organization_id, d) for d in occurrence_dates],
        )

    updated_stops = 0
    for day, route in routes.items():
        for stop in route.get("stops") or []:
            job_id = stop["job_id"]
            stop_order = stop["stop_order"]
            cur.execute(
                """
                UPDATE job_dates
                SET stop_order = %s
                WHERE job_id = %s
                  AND organization_id = %s
                  AND date >= %s
                  AND date <= %s
                  AND status = 'not_complete'
                """,
                (stop_order, job_id, organization_id, from_date, to_date),
            )
            updated_stops += cur.rowcount

    return {
        "assigned_jobs": len(assigned_job_ids),
        "updated_stop_orders": updated_stops,
    }
