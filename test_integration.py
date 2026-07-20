import unittest
import json
import os
import sqlite3
from app import app
import database

class TestPayrollIntegration(unittest.TestCase):

    def setUp(self):
        # Configure Flask app for testing
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.client = app.test_client()
        
        # Reset database for clean testing state
        if os.path.exists(database.DATABASE_FILE):
            try:
                os.remove(database.DATABASE_FILE)
            except PermissionError:
                pass # If locked by the running server
        database.init_db()

    def test_full_payroll_lifecycle_api(self):
        # 1. Fetch companies
        resp = self.client.get('/api/auth/companies')
        self.assertEqual(resp.status_code, 200)
        companies = json.loads(resp.data.decode('utf-8'))
        self.assertTrue(len(companies) >= 2)
        nexus_comp = next(c for c in companies if c['name'] == 'Nexus Corp')
        nexus_id = nexus_comp['id']

        # 2. Try adding a new company
        resp = self.client.post('/api/auth/companies', json={'name': 'Horizon Tech'})
        self.assertEqual(resp.status_code, 200)
        new_company = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(new_company['name'], 'Horizon Tech')

        # 3. Authenticate Login (Direct Login)
        resp = self.client.post('/api/auth/login', json={
            'email': 'admin@nexus.com',
            'password': 'admin123',
            'company_id': nexus_id,
            'captcha': 'test'
        })
        self.assertEqual(resp.status_code, 200)
        session_user = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(session_user['role'], 'Admin')

        # 4. Add a new employee
        resp = self.client.post('/api/employees', json={
            'employee_id_code': 'EMP801',
            'name': 'Dave Integration',
            'email': 'dave.i@nexus.com',
            'phone': '9876543200',
            'department': 'QA',
            'designation': 'Automation Specialist',
            'basic_salary': 50000.0,
            'joining_date': '2024-05-01',
            'role': 'Employee',
            'password': 'employee123'
        })
        self.assertEqual(resp.status_code, 200)
        emp_save_res = json.loads(resp.data.decode('utf-8'))
        emp_id = emp_save_res['id']

        # 5. Fetch employees to verify insertion
        resp = self.client.get('/api/employees')
        self.assertEqual(resp.status_code, 200)
        employees = json.loads(resp.data.decode('utf-8'))
        dave = next(e for e in employees if e['id'] == emp_id)
        self.assertEqual(dave['name'], 'Dave Integration')

        # 6. Apply Leave Request for Employee (unpaid)
        # Login as Dave
        resp = self.client.post('/api/auth/login', json={
            'email': 'dave.i@nexus.com',
            'password': 'employee123',
            'company_id': nexus_id,
            'captcha': 'test'
        })
        self.assertEqual(resp.status_code, 200)
        
        # Apply for 2 unpaid leave days in July 2026
        resp = self.client.post('/api/leave_requests', json={
            'start_date': '2026-07-10',
            'end_date': '2026-07-11',
            'leave_type': 'Unpaid',
            'reason': 'Moving apartments'
        })
        self.assertEqual(resp.status_code, 200)

        # Re-login as Admin to approve leave
        resp = self.client.post('/api/auth/login', json={
            'email': 'admin@nexus.com',
            'password': 'admin123',
            'company_id': nexus_id,
            'captcha': 'test'
        })
        self.assertEqual(resp.status_code, 200)

        # Fetch leave requests and approve Dave's
        resp = self.client.get('/api/leave_requests')
        self.assertEqual(resp.status_code, 200)
        leaves = json.loads(resp.data.decode('utf-8'))
        dave_leave = next(l for l in leaves if l['employee_id'] == emp_id)
        self.assertEqual(dave_leave['status'], 'Pending')

        resp = self.client.put(f"/api/leave_requests/{dave_leave['id']}", json={'status': 'Approved'})
        self.assertEqual(resp.status_code, 200)

        # 7. Generate payroll for July 2026
        # Dave has 2 unpaid leaves out of 26 working days.
        # Basic = 50,000 * 24/26 = 46,153.85
        # Gross = Basic + 40% (18,461.54) + 10% (4,615.38) + Med (1153.85) + Travel (1476.92) + Bonus (10,000) = 81,861.54
        # PF = 12% of basic = 5,538.46
        # Ins = 1000, PT = 200
        # Tax = Projected Gross: 71,861.54 * 12 + 10,000 = 872,338.48. Taxable = 872,338.48 - 75,000 = 797,338.48
        # Slabs tax: 3L-7L (4L) * 5% = 20,000; 7L-7.973L (97,338.48) * 10% = 9,733.85. Total annual = 29,733.85
        # Monthly tax = 2477.82.
        # Net = 81,861.54 - 5,538.46 - 200 - 2,477.82 - 1000 = 72,645.26
        resp = self.client.post('/api/payroll/generate', json={
            'month': 7,
            'year': 2026,
            'working_days': 26,
            'employee_ids': [emp_id],
            'bonus': 10000.0
        })
        self.assertEqual(resp.status_code, 200)
        gen_res = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(gen_res['processed_count'], 1)

        # 8. Fetch and verify payroll record
        resp = self.client.get('/api/payroll?month=7&year=2026')
        self.assertEqual(resp.status_code, 200)
        records = json.loads(resp.data.decode('utf-8'))
        dave_rec = next(r for r in records if r['employee_id'] == emp_id)
        
        self.assertEqual(dave_rec['basic_salary'], 46153.85)
        self.assertEqual(dave_rec['unpaid_leaves'], 2)
        self.assertEqual(dave_rec['bonus'], 10000.0)
        self.assertEqual(dave_rec['pf'], 5538.46)
        self.assertEqual(dave_rec['professional_tax'], 200.0)
        self.assertEqual(dave_rec['income_tax'], 2477.82)
        self.assertAlmostEqual(dave_rec['net_salary'], 72645.26, delta=1.0)

        # 9. Verify Audit Logs
        resp = self.client.get('/api/audit_logs')
        self.assertEqual(resp.status_code, 200)
        logs = json.loads(resp.data.decode('utf-8'))
        self.assertTrue(any(l['action'] == 'Generate Payroll' for l in logs))

        # 10. Verify Database Backup endpoint
        resp = self.client.get('/api/backup')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'application/x-sqlite3')

if __name__ == "__main__":
    unittest.main()
