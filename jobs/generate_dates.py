from datetime import datetime, timedelta, date


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

VALID_FREQUENCIES = {"weekly", "biweekly", "onetime"}


def parse_date(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _first_matching_weekday(start, day_of_week):
    if not day_of_week:
        return start
    target = WEEKDAYS.get(day_of_week.strip().lower())
    if target is None:
        raise ValueError(f"invalid day_of_week: {day_of_week}")
    delta = (target - start.weekday()) % 7
    return start + timedelta(days=delta)


def generate_occurrence_dates(frequency, start_date, end_date=None, day_of_week=None):
    """Return the list of occurrence dates for a job.

    onetime  -> [start_date]
    weekly    -> start_date (or first matching weekday) then every 7 days through end_date
    biweekly  -> same, every 14 days
    """
    if frequency not in VALID_FREQUENCIES:
        raise ValueError(f"invalid frequency: {frequency}")

    start = parse_date(start_date)

    if frequency == "onetime":
        return [start]

    if not end_date:
        raise ValueError("end_date is required for weekly and biweekly jobs")

    end = parse_date(end_date)
    if end < start:
        raise ValueError("end_date must be on or after start_date")

    current = _first_matching_weekday(start, day_of_week)
    step = 7 if frequency == "weekly" else 14
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=step)
    return dates
