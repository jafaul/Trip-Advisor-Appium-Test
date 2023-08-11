from datetime import datetime


class DateFormatter:
    @staticmethod
    def format_dates(input_dates: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
        dates_to_search = []
        for start_date, end_date in input_dates:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

            start_month = start_date_obj.strftime("%B %Y")
            end_month = end_date_obj.strftime("%B %Y")

            start_day = start_date_obj.strftime("%d").lstrip("0")
            end_day = end_date_obj.strftime("%d").lstrip("0")

            dates_to_search.append([(start_month, start_day), (end_month, end_day)])

        return dates_to_search
