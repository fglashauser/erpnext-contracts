# Copyright (c) 2023, PC-Giga and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from ...tools.base_enum import BaseEnum


class ContractPosition(Document):
	pass


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

    def get_timedelta(self) -> timedelta:
        """Returns the timedelta for the given billing cycle.

        Returns:
            timedelta: Timedelta.
        """
        if self == BillingCycle.Daily:
            return timedelta(days=1)
        elif self == BillingCycle.Weekly:
            return timedelta(weeks=1)
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


@frappe.whitelist()
def calculate_next_billing_date(contract_start_date: str, billing_cycle: str, valid_from: str, \
                                valid_until: str, last_billing_date: str) -> date:
    """Returns the next billing date for the given start date and frequency.

    Args:
        contract_start_date (str): Contract start date.
        billing_cycle (str): Billing cycle.
        valid_from (str): Valid from date.
        valid_until (str): Valid until date.
        last_billing_date (str): Last billing date.

    Returns:
        date: Next billing date.
    """
    # If valid from is unset, use contract start date
    if not valid_from:
        valid_from = contract_start_date

    # Mandatory: Check if billing cycle is valid
    if billing_cycle:
        billing_cycle = BillingCycle.from_str(billing_cycle)
        if not billing_cycle:
            frappe.throw("Invalid billing cycle.")
    else:
        return None

    # Mandatory: Check if valid from is valid date
    if valid_from:
        try:
            valid_from = datetime.strptime(valid_from, "%Y-%m-%d").date()
        except ValueError:
            frappe.throw("Invalid format: valid from date.")
    else:
        return None

    # Optional: Check if valid until is valid date
    if valid_until:
        try:
            valid_until = datetime.strptime(valid_until, "%Y-%m-%d").date()
        except ValueError:
            frappe.throw("Invalid format: valid until date.")

    # Optional: Check if last billing date is valid date
    if last_billing_date:
        try:
            last_billing_date = datetime.strptime(last_billing_date, "%Y-%m-%d").date()
        except ValueError:
            frappe.throw("Invalid format: last billing date.")

    # Get highest date: valid from or last billing date
    next_billing_date = max(valid_from, last_billing_date) if last_billing_date else valid_from

    # Calculate next billing date
    next_billing_date = next_billing_date + billing_cycle.get_timedelta()

    # Check if next billing date is valid until date
    if valid_until and next_billing_date > valid_until:
        return None

    return next_billing_date