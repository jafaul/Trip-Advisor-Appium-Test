import unittest

from app_testing.trip_advisor_test import TripAdvisorTest

DATES = [
    ('2023-09-01', '2023-09-02'), ('2023-09-03', '2023-09-04'),
    ('2023-09-10', '2023-09-11'), ('2023-09-04', '2023-09-05'),
    ('2023-09-28', '2023-09-29')
]

trip_advisor = TripAdvisorTest(
    input_dates=DATES,
    hotel_name="TripAdvisor"
)

