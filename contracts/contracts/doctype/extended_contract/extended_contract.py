# Copyright (c) 2023, PC-Giga and contributors
# For license information, please see license.txt

from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar
from ...tools.base_enum import BaseEnum
import frappe
from frappe import _
from frappe.model.document import Document

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class ExtendedContract(Document):
    """Business-Logic for handling extended contracts.
    """    
    def before_save(self):
        try:
            self.termination_effective_date = calculate_termination_date(
                self.is_indefinite, self.end_date, self.notice_period_amount, 
                self.notice_period_unit, self.notice_period_term)
        except Exception as e:
            frappe.throw(f"Error while saving: {e}")

    def get_unbilled_positions(self):
        """Returns the unbilled positions for the contract.
        """
        positions = []
        for position in self.positions:
            if not position.billed:
                positions.append(position)
        return positions


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


class NoticePeriodUnit(BaseEnum):
    """Enumeration for the notice period unit.
    """
    Days    = "day(s)"
    Weeks   = "week(s)"
    Months  = "month(s)"
    Years   = "year(s)"

    def get_timedelta(self, amount: int) -> timedelta:
        """Returns the timedelta for the given notice period unit.

        Args:
            amount (int): Amount of the notice period.

        Returns:
            timedelta: Timedelta.
        """
        if self == NoticePeriodUnit.Days:
            return timedelta(days=amount)
        elif self == NoticePeriodUnit.Weeks:
            return timedelta(weeks=amount)
        elif self == NoticePeriodUnit.Months:
            return relativedelta(months=amount)
        elif self == NoticePeriodUnit.Years:
            return relativedelta(years=amount)


@frappe.whitelist()
def calculate_termination_date(is_indefinite: bool, end_date, np_amount, np_unit, np_term) -> date:
    """Calculates the termination effective date and returns it.
    Used for javascript calculation on field change.

    Args:
        is_indefinite (bool): Is the contract indefinite?
        end_date (date): End date of the contract.
        np_amount (int): Notice period amount.
        np_unit (str): Notice period unit.
        np_term (str): Notice period term.

    Returns:
        date: Termination effective date.
    """
    termination_date = None

    # No termination date if not indefinite
    if not is_indefinite:
        return None

    # No termination date if no minimum runtime
    if not end_date:
        return None

    # Convert end date to date object
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # If no notice period term, use end date
    if not np_term:
        termination_date = end_date
    else:
        termination_date = get_last_day_of_period(end_date, NoticePeriodTerm.from_str(np_term))

    # Subtract notice period delta
    if np_amount and np_unit:
        termination_date = termination_date - NoticePeriodUnit.from_str(np_unit).get_timedelta(np_amount)

    return termination_date
    
@frappe.whitelist()
def get_item_details(item_code: str) -> dict:
    """Returns the item details for the given item code.

    Args:
        item_code (str): Item code.

    Returns:
        dict: Item details.
    """
    item = frappe.get_doc("Item", item_code)
    return {
        "item_name": item.item_name,
        "description": item.description,
        "uom": item.stock_uom,
        "price_list_rate": item.price_list_rate,
        "standard_rate": item.standard_rate,
        "default_warehouse": item.default_warehouse
    }

def get_last_day_of_period(end_date: date, period_term: NoticePeriodTerm):
    """Returns the last day of the period.
    """
    # before Contract end: return minimum runtime
    if period_term == NoticePeriodTerm.BeforeContractEnd:
        return end_date

    # at Month's end: return last day of month of minimum runtime
    elif period_term == NoticePeriodTerm.AtMonthEnd:
        month_days = calendar.monthrange(end_date.year, end_date.month)
        return date(end_date.year, end_date.month, month_days[1])

    # at Quarter's end: return last day of quarter of minimum runtime
    elif period_term == NoticePeriodTerm.AtQuarterEnd:
        quarter = (end_date.month - 1) // 3 + 1
        return date(end_date.year, quarter * 3, calendar.monthrange(end_date.year, quarter * 3)[1])

    # at Calendar year end: return last day of year of minimum runtime
    elif period_term == NoticePeriodTerm.AtCalendarYearEnd:
        return date(end_date.year, 12, 31)

    # on 15th of month: return 15th of month (or next if already passed) of minimum runtime
    elif period_term == NoticePeriodTerm.On15th:
        if end_date.day > 15:
            end_date = end_date + relativedelta(months=1)
        return date(end_date.year, end_date.month, 15)

    # on 15th or end of month: return 15th of month (or next if already passed) of minimum runtime
    elif period_term == NoticePeriodTerm.On15OrEnd:
        return date(end_date.year, end_date.month, 15 if end_date.day <= 15 \
                    else calendar.monthrange(end_date.year, end_date.month)[1])

    # at mid-year: returns 30/06 or 31/12 starting from minimum runtime
    elif period_term == NoticePeriodTerm.AtMidYear:
        return date(end_date.year, 6, 30) if end_date.month <= 6 \
                    else date(end_date.year, 12, 31)
    