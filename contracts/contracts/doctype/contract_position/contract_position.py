# Copyright (c) 2023, PC-Giga and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.model.document import Document
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from ...tools.base_enum import BaseEnum
from ..extended_contract.billing_type import BillingType
#from .billing_position import BillingPosition
from .billing_cycle import BillingCycle
from .billing_period import BillingPeriod


class ContractPosition(Document):
    def _billing_periods(self):
        if self._billing_periods:
            return self._billing_periods
        # TODO: Implement

        


    def min_billable_date(self) -> date:
        """Returns the minimum billable date for the given contract position.
        """
        contract = frappe.get_doc("Extended Contract", self.parent)
        if not contract.start_date:
            return None
        if not self.valid_from:
            self.valid_from = contract.start_date
        contract_start_date = utils.getdate(contract.start_date)
        valid_from          = utils.getdate(self.valid_from)
        last_billing_date   = utils.getdate(self.last_billing_date) if self.last_billing_date else None
        min_date            = max(contract_start_date, valid_from, last_billing_date) \
                            if last_billing_date else max(contract_start_date, valid_from)
        # TODO: Logikfehler: Wenn last_billing_date nicht Perioden-Start, dann verschiebt sich Perioden-Start
        return min_date
    
    def max_billable_date(self) -> date:
        """Returns the maximum billable date for the given contract position.
        """
        contract = frappe.get_doc("Extended Contract", self.parent)
        if not contract.end_date or (contract.is_indefinite and not self.valid_until):
            return date.today()
        if not self.valid_until:
            self.valid_until = contract.end_date
        contract_end_date   = utils.getdate(contract.end_date)
        valid_until         = utils.getdate(self.valid_until)
        return min(contract_end_date, valid_until)

    # def get_billable_positions(self) -> list(BillingPosition):
    #     """Returns a list of billing positions for the given contract position.
    #     """
    #     contract = frappe.get_doc("Extended Contract", self.parent)
    #     min_billable_date = self.min_billable_date()
    #     max_billable_date = self.max_billable_date()

    #     # Required: min billable date
    #     if not min_billable_date:
    #         return []

    #     # Required: billing cycle
    #     billing_cycle = BillingCycle.from_str(self.billing_cycle)
    #     if not billing_cycle:
    #         return []
        
    #     # Required: billing type (billable or not)
    #     billing_type = BillingType.from_str(contract.billing_type)
    #     if not billing_type or billing_type == BillingType.NotBilllable:
    #         return []
        

    #     # Create billing positions
    #     positions = []
    #     curr_date = min_billable_date
    #     while curr_date <= max_billable_date:
    #         positions.append(BillingPosition(
    #             contract_position=self,
    #             billing_period=BillingPeriod(curr_date, billing_cycle)
    #         ))
    #         curr_date += billing_cycle.get_timedelta()
        

    def get_next_billing_date(self) -> date:
        """Returns the next billing date for the given contract position.
        """
        unbilled_positions = self.get_unbilled_positions()
        if not unbilled_positions or len(unbilled_positions) == 0:
            return None
        



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
        "rate": item.standard_rate
    }