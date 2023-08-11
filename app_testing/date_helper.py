from app_testing.date_calculator import DateCalculator


class DateHelper:
    @staticmethod
    def get_output_dates(dates: list[tuple[str, str]]) -> str:
        row_arrival_month_and_year, arrival_day = dates[0]
        row_departure_month_and_year, departure_day = dates[1]

        arrival_month_and_year = row_arrival_month_and_year.split(' ')
        departure_month_and_year = row_departure_month_and_year.split(' ')

        arrival_month = DateCalculator.get_month_number(arrival_month_and_year[0])
        arrival_year = arrival_month_and_year[1]

        departure_month = DateCalculator.get_month_number(departure_month_and_year[0])
        departure_year = departure_month_and_year[1]

        formatted_date = \
            f"{arrival_day}_{arrival_month}_{arrival_year}-{departure_day}_{departure_month}_{departure_year}"

        return formatted_date


