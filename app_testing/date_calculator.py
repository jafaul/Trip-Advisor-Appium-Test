from datetime import datetime


class DateCalculator:
    @staticmethod
    def get_month_number(month: str) -> str:
        return datetime.strptime(month, "%B").strftime("%m")

    @staticmethod
    def is_current_calendar_position_before_or_after_desired(
            current_calendar_position: str, desired_calendar_position: str
    ) -> str | bool:
        current_date = datetime.strptime(current_calendar_position, '%B %Y')
        desired_date = datetime.strptime(desired_calendar_position, '%B %Y')

        if current_date < desired_date:
            return "before"

        if current_date > desired_date:
            return "after"

        if current_date.year == desired_date.year and current_date.month == desired_date.month:
            return False
