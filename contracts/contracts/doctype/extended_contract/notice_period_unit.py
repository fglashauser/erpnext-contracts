from ...tools.base_enum import BaseEnum
from dateutil.relativedelta import relativedelta

class NoticePeriodUnit(BaseEnum):
    """Enumeration for the notice period unit.
    """
    Days    = "day(s)"
    Weeks   = "week(s)"
    Months  = "month(s)"
    Years   = "year(s)"

    def get_timedelta(self, amount: int) -> relativedelta:
        """Returns the timedelta for the given notice period unit.

        Args:
            amount (int): Amount of the notice period.

        Returns:
            timedelta: Timedelta.
        """
        if self == NoticePeriodUnit.Days:
            return relativedelta(days=amount)
        elif self == NoticePeriodUnit.Weeks:
            return relativedelta(weeks=amount)
        elif self == NoticePeriodUnit.Months:
            return relativedelta(months=amount)
        elif self == NoticePeriodUnit.Years:
            return relativedelta(years=amount)