# Copyright (c) 2023, PC-Giga and contributors
# For license information, please see license.txt

from datetime import date
from dateutil.relativedelta import relativedelta
import calendar
import frappe
from frappe import _, utils
from frappe.model.document import Document

# from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
# from erpnext.accounts.doctype.payment_schedule.payment_schedule import PaymentSchedule
# from erpnext.accounts.doctype.payment_term.payment_term import PaymentTerm
# from erpnext.accounts.doctype.mode_of_payment.mode_of_payment import ModeofPayment

from ..contract_position.billing_cycle import BillingCycle
#from .billing_type import BillingType
from .notice_period_term import NoticePeriodTerm
from .notice_period_unit import NoticePeriodUnit
#from ..contract_position.contract_position import ContractPosition


class ExtendedContract(Document):
    """Business-Logic for handling extended contracts.
    """
    def before_save(self):
        self.update_termination_date()

    @frappe.whitelist()
    def update_termination_date(self) -> date:
        """Updates the termination effective date and returns it.

        Returns:
            date: Termination effective date.
        """
        # No termination date if not indefinite
        if not self.is_indefinite:
            return None

        # No termination date if no minimum runtime
        if not self.end_date:
            return None
        
        # Validate & convert end date
        self.end_date = utils.getdate(self.end_date)

        # If no notice period term, use end date
        if not self.np_term:
            self.termination_effective_date = self.end_date
        else:
            self.termination_effective_date = get_last_day_of_notice_period(self.end_date, \
                                                             NoticePeriodTerm.from_str(self.np_term))

        # Subtract notice period delta
        if self.np_amount and self.np_unit:
            self.termination_effective_date = self.termination_effective_date - \
                NoticePeriodUnit.from_str(self.np_unit).get_timedelta(int(self.np_amount))

        return self.termination_effective_date

    @frappe.whitelist()
    def get_position_next_billing_date(self, position_dict: dict) -> date:
        """Calculates the next billing date of the given position and returns it.

        Args:
            position_dict: Contract position to update

        Returns:
            date: Next billing date.
        """
        position = frappe.get_doc("Contract Position", position_dict)
        return position.get_next_billing_date()

        # # Check if contract is billable
        # billing_type = BillingType.from_str(self.billing_type)
        # if not billing_type or billing_type == BillingType.NotBilllable:
        #     return None
        
        # # Required: contract start date
        # if not self.start_date:
        #     return None
        
        # # Required: billing cycle
        # billing_cycle = BillingCycle.from_str(position.get('billing_cycle', None))
        # if not billing_cycle:
        #     return None

        # # If valid from is unset, use contract start date
        # if not position.get('valid_from', None):
        #     position['valid_from'] = self.start_date

        # # Validate & convert dates
        # valid_from          = utils.getdate(position['valid_from'])
        # contract_start_date = utils.getdate(self.start_date)
        # contract_end_date   = utils.getdate(self.end_date) if self.end_date else None                                           # optional
        # valid_until         = utils.getdate(position['valid_until']) if position.get('valid_until', None) else None             # optional
        # last_billing_date   = utils.getdate(position['last_billing_date']) if position.get('last_billing_date', None) else None # optional

        # # If valid from is before contract start date, use contract start date
        # if valid_from < contract_start_date:
        #     valid_from = contract_start_date

        # # Get billing day (first or last day depending on billing type)
        # billing_day = get_first_day_of_billing_period(valid_from, billing_cycle, last_billing_date) \
        #     if billing_type == BillingType.BeforeBillingPeriod \
        #     else get_last_day_of_billing_period(valid_from, billing_cycle, last_billing_date)

        # # Check if date is in valid range
        # if valid_until and billing_day > valid_until:
        #     return None
        # if billing_day < contract_start_date:
        #     return None
        # if not self.is_indefinite and contract_end_date and billing_day > contract_end_date:
        #     return None
        
        # return billing_day

    
    @frappe.whitelist()
    def create_invoices(self):
        """Creates invoices for all unbilled positions.
        """
        return self.create_invoice()
    
    def create_invoice(self):
        """Creates an invoice for all unbilled positions.
        """
        # Get unbilled positions
        positions = self.get_unbilled_positions()

        # Create invoice
        invoice = frappe.new_doc("Sales Invoice")
        invoice.title = self.commission
        invoice.customer = self.customer
        invoice.posting_date = date.today()
        invoice.due_date = date.today()
        # invoice.due_date = max([ps.due_date for ps in self.payment_schedule]) \
        #     if len(self.payment_schedule) > 0 else date.today()
        invoice.set_posting_time = 1
        invoice.ignore_pricing_rule = 1
        invoice.update_stock = 0
        #invoice.payment_schedule = self.payment_schedule
        invoice.extended_contract = self.name

        # Add items
        for position in positions:
            invoice.append('items', {
                'item_code': position.item,
                'item_name': position.item_name,
                'description': position.description,
                'uom': position.uom,
                'qty': position.quantity,
                'rate': position.rate,
                'discount_percentage': position.discount_percentage,
                'income_account': self.income_account
            })
        
        # Set taxes
        invoice.set_taxes()

        # Update positions
        for position in positions:
            position.last_billing_date = position.next_billing_date
            position.next_billing_date = self.get_next_billing_date(vars(position))

        # Save contract
        self.save()

        # Save invoice
        invoice.set_missing_values()
        return invoice.insert()


def get_last_day_of_notice_period(end_date: date, period_term: NoticePeriodTerm) -> date:
    """Returns the last day of the notice period.
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
    

def get_first_day_of_billing_period(valid_from: date, billing_cycle: BillingCycle, last_billing_date: date = None) -> date:
    """Returns the first day of the period for the given contract position.

    Args:
        valid_from (date): Position valid from date
        billing_cycle (BillingCycle): Position billing cycle
        last_billing_date (date): Position last billing date

    Returns:
        date: First day of the period.
    """
    if not last_billing_date:
        return valid_from
    
    curr_date = valid_from
    while curr_date < last_billing_date + relativedelta(days=1):
        curr_date = curr_date + billing_cycle.get_timedelta()

    return curr_date


def get_last_day_of_billing_period(valid_from: date, billing_cycle: BillingCycle, last_billing_date: date = None) -> date:
    """Returns the last day of the period for the given contract position.

    Args:
        valid_from (date): Position valid from date
        billing_cycle (BillingCycle): Position billing cycle
        last_billing_date (date): Position last billing date

    Returns:
        date: Last day of the period.
    """
    if not last_billing_date and billing_cycle == BillingCycle.Daily:
        return valid_from
    if not last_billing_date:
        return valid_from + billing_cycle.get_timedelta() - relativedelta(days=1)
    
    curr_date = valid_from + billing_cycle.get_timedelta() - relativedelta(days=1)
    while curr_date < last_billing_date + billing_cycle.get_timedelta():
        curr_date = curr_date + billing_cycle.get_timedelta()
    
    return curr_date