from ...tools.base_enum import BaseEnum

class NoticePeriodTerm(BaseEnum):
    """Enumeration for the notice period term.
    """
    BeforeContractEnd   = "before Contract end"
    AtMonthEnd          = "at Month's end"
    AtQuarterEnd        = "at Quarter's end"
    AtCalendarYearEnd   = "at Calendar year end"
    On15th              = "on 15th of month"
    On15OrEnd           = "on 15th or end of month"
    AtMidYear           = "at mid-year"