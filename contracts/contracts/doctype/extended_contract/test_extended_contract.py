# Copyright (c) 2023, PC-Giga and Contributors
# See license.txt

from datetime import date
from frappe.tests.utils import FrappeTestCase
import frappe
import unittest

from .extended_contract import (
    get_last_day_of_period,
    calculate_termination_date,
    NoticePeriodTerm,
    NoticePeriodUnit
)

class TestExtendedContract(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_last_day_of_period(self):
        end_date = date(2024, 7, 11)

        # before Contract end
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.BeforeContractEnd)
        self.assertEqual(last_day, date(2024, 7, 11))

        # at Month's end
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.AtMonthEnd)
        self.assertEqual(last_day, date(2024, 7, 31))

        # at Quarter's end
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.AtQuarterEnd)
        self.assertEqual(last_day, date(2024, 9, 30))

        # at Calendar year end
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.AtCalendarYearEnd)
        self.assertEqual(last_day, date(2024, 12, 31))

        # on 15th of month
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.On15th)
        self.assertEqual(last_day, date(2024, 7, 15))
        last_day = get_last_day_of_period(date(2024, 7, 16), NoticePeriodTerm.On15th)
        self.assertEqual(last_day, date(2024, 8, 15))

        # on 15th or end of month
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.On15OrEnd)
        self.assertEqual(last_day, date(2024, 7, 15))
        last_day = get_last_day_of_period(date(2024, 7, 16), NoticePeriodTerm.On15OrEnd)
        self.assertEqual(last_day, date(2024, 7, 31))

        # at mid-year
        last_day = get_last_day_of_period(end_date, NoticePeriodTerm.AtMidYear)
        self.assertEqual(last_day, date(2024, 12, 31))
        last_day = get_last_day_of_period(date(2024, 6, 1), NoticePeriodTerm.AtMidYear)
        self.assertEqual(last_day, date(2024, 6, 30))


    def test_calculate_termination_date(self):
        is_indefinite   = True
        end_date        = date(2024, 7, 11)
        np_amount       = 3
        np_unit         = NoticePeriodUnit.Months.value
        np_term         = NoticePeriodTerm.BeforeContractEnd.value

        # No Indefinite contract
        result = calculate_termination_date(False, end_date, np_amount, np_unit, np_term)
        self.assertEqual(result, None)

        # No minimum runtime
        result = calculate_termination_date(is_indefinite, None, np_amount, np_unit, np_term)
        self.assertEqual(result, None)

        # No notice period term -> should be end_date - np_amount
        result = calculate_termination_date(is_indefinite, end_date, np_amount, np_unit, None)
        self.assertEqual(result, date(2024, 4, 11))

        # Only term: before Contract end
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.BeforeContractEnd.value)
        self.assertEqual(result, date(2024, 7, 11))

        # Only term: at Month's end
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.AtMonthEnd.value)
        self.assertEqual(result, date(2024, 7, 31))

        # Only term: at Quarter's end
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.AtQuarterEnd.value)
        self.assertEqual(result, date(2024, 9, 30))

        # Only term: at Calendar year end
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.AtCalendarYearEnd.value)
        self.assertEqual(result, date(2024, 12, 31))

        # Only term: on 15th of month
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.On15th.value)
        self.assertEqual(result, date(2024, 7, 15))

        # Only term: on 15th or end of month
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.On15OrEnd.value)
        self.assertEqual(result, date(2024, 7, 15))
        result = calculate_termination_date(is_indefinite, date(2024, 7, 15), None, None, NoticePeriodTerm.On15OrEnd.value)
        self.assertEqual(result, date(2024, 7, 15))
        result = calculate_termination_date(is_indefinite, date(2024, 7, 16), None, None, NoticePeriodTerm.On15OrEnd.value)
        self.assertEqual(result, date(2024, 7, 31))

        # Only term: at mid-year
        result = calculate_termination_date(is_indefinite, end_date, None, None, NoticePeriodTerm.AtMidYear.value)
        self.assertEqual(result, date(2024, 12, 31))
        result = calculate_termination_date(is_indefinite, date(2024, 5, 23), None, None, NoticePeriodTerm.AtMidYear.value)
        self.assertEqual(result, date(2024, 6, 30))

        # Subtract notice period: days
        result = calculate_termination_date(is_indefinite, end_date, 11, NoticePeriodUnit.Days.value, np_term)
        self.assertEqual(result, date(2024, 6, 30))

        # Subtract notice period: weeks
        result = calculate_termination_date(is_indefinite, end_date, 2, NoticePeriodUnit.Weeks.value, np_term)
        self.assertEqual(result, date(2024, 6, 27))

        # Subtract notice period: months
        result = calculate_termination_date(is_indefinite, end_date, 8, NoticePeriodUnit.Months.value, np_term)
        self.assertEqual(result, date(2023, 11, 11))

        # Subtract notice period: years
        result = calculate_termination_date(is_indefinite, end_date, 1, NoticePeriodUnit.Years.value, np_term)
        self.assertEqual(result, date(2023, 7, 11))