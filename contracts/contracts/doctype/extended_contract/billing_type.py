from ...tools.base_enum import BaseEnum

class BillingType(BaseEnum):
    """Enumeration for the billing type.
    """
    BeforeBillingPeriod     = "Create invoice before billing period"
    AfterBillingPeriod      = "Create invoice after billing period"
    NotBilllable            = "Not billable"