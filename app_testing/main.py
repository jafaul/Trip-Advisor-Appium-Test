from app_testing.trip_advisor_test import TripAdvisorTest


dates = [
    ('2023-12-31', '2024-01-01'), ('2023-09-27', '2023-09-28'), ('2023-10-28', '2023-10-29'),
    ('2023-11-10', '2023-11-11'), ('2023-12-24', '2023-12-25'),
]


def test_run():
    test_scenario = TripAdvisorTest(hotel_name="The Grosvenor Hotel", input_dates=dates)
    test_scenario.run_test()
