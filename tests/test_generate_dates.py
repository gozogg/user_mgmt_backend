from datetime import date

import pytest

from jobs.generate_dates import generate_occurrence_dates


def test_onetime_returns_start_date_only():
    assert generate_occurrence_dates("onetime", "2026-03-10") == [date(2026, 3, 10)]


def test_weekly_aligns_to_weekday_and_steps_by_seven():
    dates = generate_occurrence_dates(
        "weekly",
        "2026-03-09",  # Monday
        end_date="2026-03-30",
        day_of_week="wednesday",
    )
    assert dates == [
        date(2026, 3, 11),
        date(2026, 3, 18),
        date(2026, 3, 25),
    ]


def test_biweekly_steps_by_fourteen():
    dates = generate_occurrence_dates(
        "biweekly",
        "2026-03-02",
        end_date="2026-03-30",
        day_of_week="monday",
    )
    assert dates == [
        date(2026, 3, 2),
        date(2026, 3, 16),
        date(2026, 3, 30),
    ]


def test_weekly_requires_end_date():
    with pytest.raises(ValueError, match="end_date"):
        generate_occurrence_dates("weekly", "2026-03-01")


def test_invalid_frequency_raises():
    with pytest.raises(ValueError, match="invalid frequency"):
        generate_occurrence_dates("monthly", "2026-03-01")
