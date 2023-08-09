from datetime import datetime


class DateHelper:
    @staticmethod
    def format_dates(input_dates: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
        dates_to_search = []
        for start_date, end_date in input_dates:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

            month = start_date_obj.strftime("%B %Y")

            start_day = start_date_obj.strftime("%d").lstrip("0")
            end_day = end_date_obj.strftime("%d").lstrip("0")

            dates_to_search.append([(month, start_day), (month, end_day)])

        return dates_to_search

    @staticmethod
    def get_current_month_and_year() -> str:
        now = datetime.now()
        month_name = now.strftime("%B")
        year = now.strftime("%Y")
        return f"{month_name} {year}"

    @staticmethod
    def get_output_dates(dates: list[tuple[str, str]]) -> str:
        row_arrival_month_and_year, arrival_day = dates[0]
        row_departure_month_and_year, departure_day = dates[1]

        def get_month_number(month: str) -> str:
            return datetime.strptime(month, "%B").strftime("%m")

        arrival_month_and_year = row_arrival_month_and_year.split(' ')
        departure_month_and_year = row_departure_month_and_year.split(' ')

        arrival_month = get_month_number(arrival_month_and_year[0])
        arrival_year = arrival_month_and_year[1]

        departure_month = get_month_number(departure_month_and_year[0])
        departure_year = departure_month_and_year[1]

        formatted_date = f"{arrival_day}_{arrival_month}_{arrival_year}-{departure_day}_{departure_month}_{departure_year}"

        return formatted_date
