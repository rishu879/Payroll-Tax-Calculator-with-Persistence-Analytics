import unittest
from salary_engine import calculate_payroll_details

class TestSalaryEngine(unittest.TestCase):

    def setUp(self):
        # Default tax slabs representing FY 2025-26 New Tax Regime
        self.tax_slabs = [
            {'min_income': 0.0, 'max_income': 300000.0, 'tax_rate': 0.00},
            {'min_income': 300000.0, 'max_income': 700000.0, 'tax_rate': 0.05},
            {'min_income': 700000.0, 'max_income': 1000000.0, 'tax_rate': 0.10},
            {'min_income': 1000000.0, 'max_income': 1500000.0, 'tax_rate': 0.15},
            {'min_income': 1500000.0, 'max_income': None, 'tax_rate': 0.20}
        ]

    def test_standard_salary_calculation_no_tax(self):
        # Basic = 30,000, 26 working days, 0 leaves
        # Gross = 30000 (basic) + 12000 (hra 40%) + 3000 (da 10%) + 1250 (med) + 1600 (travel) = 47,850
        # Projected annual gross = 47850 * 12 = 5,74,200
        # Taxable income = 5,74,200 - 75,000 = 4,99,200. Since annual gross (574200) - std (75000) = 499200 <= 700000, tax is 0.
        # PF = 12% of basic = 3,600
        # PT = 200
        # Insurance = 1000
        # Net = 47850 - 3600 - 200 - 0 - 1000 = 43,050
        res = calculate_payroll_details(
            basic_salary=30000.0,
            bonus=0.0,
            working_days=26,
            unpaid_leaves=0,
            tax_slabs=self.tax_slabs
        )
        self.assertEqual(res['gross_salary'], 47850.0)
        self.assertEqual(res['pf'], 3600.0)
        self.assertEqual(res['professional_tax'], 200.0)
        self.assertEqual(res['income_tax'], 0.0)
        self.assertEqual(res['net_salary'], 43050.0)

    def test_salary_pro_rated_with_leaves(self):
        # Basic = 60,000, 26 working days, 2 unpaid leaves -> prorate_factor = 24 / 26
        # Prorated Basic = 60000 * 24 / 26 = 55,384.62
        # Prorated HRA = 24000 * 24 / 26 = 22,153.85
        # Prorated DA = 6000 * 24 / 26 = 5,538.46
        # Prorated Med = 1250 * 24 / 26 = 1,153.85
        # Prorated Travel = 1600 * 24 / 26 = 1,476.92
        # Gross = 55384.62 + 22153.85 + 5538.46 + 1153.85 + 1476.92 = 85,707.70
        res = calculate_payroll_details(
            basic_salary=60000.0,
            bonus=0.0,
            working_days=26,
            unpaid_leaves=2,
            tax_slabs=self.tax_slabs
        )
        self.assertEqual(res['basic_salary'], 55384.62)
        self.assertEqual(res['gross_salary'], 85707.69)
        self.assertEqual(res['pf'], 6646.15) # 12% of 55,384.62

    def test_progressive_tax_calculation(self):
        # Basic = 90,000, 0 leaves, 0 bonus
        # Regular monthly gross = 90000 (basic) + 36000 (hra) + 9000 (da) + 1250 (med) + 1600 (travel) = 1,37,850
        # Projected annual gross = 137850 * 12 = 16,54,200
        # Taxable income = 1654200 - 75000 = 15,79,200
        # Slabs check:
        # 0-3L: 0
        # 3L-7L (4L): 5% = 20,000
        # 7L-10L (3L): 10% = 30,000
        # 10L-15L (5L): 15% = 75,000
        # 15L-15.792L (79,200): 20% = 15,840
        # Total annual tax = 20000 + 30000 + 75000 + 15840 = 1,40,840
        # Monthly tax = 140840 / 12 = 11,736.67
        res = calculate_payroll_details(
            basic_salary=90000.0,
            bonus=0.0,
            working_days=26,
            unpaid_leaves=0,
            tax_slabs=self.tax_slabs
        )
        self.assertEqual(res['projected_annual_gross'], 1654200.0)
        self.assertEqual(res['taxable_income'], 1579200.0)
        self.assertEqual(res['annual_tax'], 140840.0)
        self.assertEqual(res['income_tax'], 11736.67)

if __name__ == "__main__":
    unittest.main()
