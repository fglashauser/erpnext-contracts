from datetime import date
from .billing_cycle import BillingCycle
from ..extended_contract.billing_type import BillingType
from dateutil.relativedelta import relativedelta

class BillingPeriod:
    """Represents a billing period of a contract position.
    """
    def __init__(self, first_day: date, billing_cycle: BillingCycle):
        self.first_day = first_day
        self.billing_cycle = billing_cycle
        self.last_day = self.first_day + self.billing_cycle.get_timedelta() - relativedelta(days=1)
        

    # def first_day(self) -> date:
    #     """Returns the first day of the billing period.
    #     """
    #     if self.billing_type == BillingType.NotBilllable:
    #         return None
    #     elif self.billing_type == BillingType.BeforeBillingPeriod or \
    #         self.billing_cycle == BillingCycle.Daily:
    #         return self.billing_day
    #     elif self.billing_type == BillingType.AfterBillingPeriod:
    #         return self.billing_day - self.billing_cycle.get_timedelta() + relativedelta(days=1)

    # def last_day(self) -> date:
    #     """Returns the last day of the billing period.
    #     """
    #     if self.billing_type == BillingType.NotBilllable:
    #         return None
    #     elif self.billing_type == BillingType.AfterBillingPeriod or \
    #         self.billing_cycle == BillingCycle.Daily:
    #         return self.billing_day
    #     elif self.billing_type == BillingType.BeforeBillingPeriod:
    #         return self.billing_day + self.billing_cycle.get_timedelta() - relativedelta(days=1)