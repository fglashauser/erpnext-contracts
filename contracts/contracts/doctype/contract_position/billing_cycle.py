from ...tools.base_enum import BaseEnum
from dateutil.relativedelta import relativedelta

class BillingCycle(BaseEnum):
    """Enumeration for the billing cycle.
    """
    Daily       = "daily"
    Weekly      = "weekly"
    Monthly     = "monthly"
    Quarterly   = "1/4 year"
    Halfyearly  = "1/2 year"
    Yearly      = "yearly"
    TwoYears    = "2 years"
    ThreeYears  = "3 years"
    FourYears   = "4 years"
    FiveYears   = "5 years"

    def get_timedelta(self) -> relativedelta:
        """Returns the timedelta for the given billing cycle.

        Returns:
            timedelta: Timedelta.
        """
        if self == BillingCycle.Daily:
            return relativedelta(days=1)
        elif self == BillingCycle.Weekly:
            return relativedelta(weeks=1)
        elif self == BillingCycle.Monthly:
            return relativedelta(months=1)
        elif self == BillingCycle.Quarterly:
            return relativedelta(months=3)
        elif self == BillingCycle.Halfyearly:
            return relativedelta(months=6)
        elif self == BillingCycle.Yearly:
            return relativedelta(years=1)
        elif self == BillingCycle.TwoYears:
            return relativedelta(years=2)
        elif self == BillingCycle.ThreeYears:
            return relativedelta(years=3)
        elif self == BillingCycle.FourYears:
            return relativedelta(years=4)
        elif self == BillingCycle.FiveYears:
            return relativedelta(years=5)