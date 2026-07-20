import sqlite3
import os
from datetime import datetime

DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payroll.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Companies Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            employee_id_code TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            phone_verified INTEGER DEFAULT 0, -- 0 for Unverified, 1 for Verified
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            basic_salary REAL NOT NULL,
            joining_date TEXT NOT NULL,
            role TEXT DEFAULT 'Employee', -- 'Admin', 'Employee', 'HR Manager', 'Finance Manager', 'Payroll Manager'
            password TEXT NOT NULL, -- Simple text passwords for demo/simplicity
            status TEXT DEFAULT 'Active', -- 'Active' or 'Inactive'
            
            -- Extended fields
            gender TEXT DEFAULT 'Male',
            father_name TEXT,
            mother_name TEXT,
            dob TEXT,
            age INTEGER,
            blood_group TEXT,
            emergency_contact TEXT,
            experience REAL DEFAULT 0,
            education TEXT,
            pan_number TEXT,
            aadhaar_number TEXT,
            bank_account TEXT,
            ifsc_code TEXT,
            photo TEXT,
            address TEXT,
            state TEXT,
            city TEXT,
            country TEXT,
            pin_code TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            UNIQUE(company_id, email),
            UNIQUE(company_id, employee_id_code)
        )
    """)

    # Schema migration to add missing columns in case DB already exists
    columns_to_add = [
        ("phone_verified", "INTEGER DEFAULT 0"),
        ("gender", "TEXT DEFAULT 'Male'"),
        ("father_name", "TEXT"),
        ("mother_name", "TEXT"),
        ("dob", "TEXT"),
        ("age", "INTEGER"),
        ("blood_group", "TEXT"),
        ("emergency_contact", "TEXT"),
        ("experience", "REAL DEFAULT 0"),
        ("education", "TEXT"),
        ("pan_number", "TEXT"),
        ("aadhaar_number", "TEXT"),
        ("bank_account", "TEXT"),
        ("ifsc_code", "TEXT"),
        ("photo", "TEXT"),
        ("address", "TEXT"),
        ("state", "TEXT"),
        ("city", "TEXT"),
        ("country", "TEXT"),
        ("pin_code", "TEXT")
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE employees ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # 3. Tax Slabs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tax_slabs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            min_income REAL NOT NULL,
            max_income REAL, -- NULL for upper open-ended slab
            tax_rate REAL NOT NULL, -- Rate as decimal, e.g. 0.05 for 5%
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 4. Payroll Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            basic_salary REAL NOT NULL,
            hra REAL NOT NULL,
            da REAL NOT NULL,
            bonus REAL DEFAULT 0.0,
            medical_allowance REAL DEFAULT 0.0,
            travel_allowance REAL DEFAULT 0.0,
            gross_salary REAL NOT NULL,
            pf REAL NOT NULL,
            professional_tax REAL DEFAULT 0.0,
            income_tax REAL NOT NULL,
            insurance REAL DEFAULT 0.0,
            net_salary REAL NOT NULL,
            working_days INTEGER NOT NULL,
            paid_leaves INTEGER DEFAULT 0,
            unpaid_leaves INTEGER DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE(employee_id, month, year)
        )
    """)

    # 5. Leave Requests Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            leave_type TEXT NOT NULL, -- 'Paid', 'Unpaid', 'Sick'
            reason TEXT,
            status TEXT DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
    """)

    # 6. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 7. HR Recruitment Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recruitment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            candidate_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            designation TEXT NOT NULL,
            status TEXT DEFAULT 'Applied', -- 'Applied', 'Interviewing', 'Offer Letter', 'Joined', 'Rejected'
            feedback TEXT,
            interview_date TEXT,
            offer_letter_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 8. Daily Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL, -- YYYY-MM-DD
            clock_in TEXT,
            clock_out TEXT,
            late_entry INTEGER DEFAULT 0, -- in minutes
            overtime_hours REAL DEFAULT 0.0,
            status TEXT NOT NULL, -- 'Present', 'Absent', 'Half Day', 'Holiday'
            FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE(employee_id, date)
        )
    """)

    # 9. Finance Table (Company income/expenses)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'Income', 'Expense'
            category TEXT NOT NULL, -- 'Payroll', 'Bonus', 'Tax Paid', 'Operational', 'Revenue'
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL, -- YYYY-MM-DD
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 10. Department Budgets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department_budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            budget REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            UNIQUE(company_id, department, month, year)
        )
    """)

    # 11. Suppliers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            company TEXT,
            gst_number TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            payment_terms TEXT,
            outstanding_balance REAL DEFAULT 0.0,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 12. Inventory Table (Company assets & supplies)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            sku_code TEXT,
            barcode TEXT,
            category TEXT NOT NULL, -- 'Laptops', 'Desktops', 'Furniture', 'Networking', 'Accessories'
            brand TEXT,
            model TEXT,
            serial_number TEXT,
            description TEXT,
            purchase_date TEXT,
            purchase_price REAL DEFAULT 0.0,
            selling_price REAL DEFAULT 0.0,
            gst REAL DEFAULT 18.0,
            supplier_id INTEGER,
            warehouse TEXT DEFAULT 'Warehouse A', -- 'Warehouse A', 'Warehouse B', 'Branch Office'
            location TEXT,
            current_stock INTEGER DEFAULT 1,
            minimum_stock INTEGER DEFAULT 1,
            maximum_stock INTEGER DEFAULT 10,
            status TEXT DEFAULT 'Available', -- 'Available', 'Assigned', 'Under Maintenance', 'Damaged'
            warranty_expiry TEXT,
            assigned_employee_id INTEGER,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
            FOREIGN KEY(assigned_employee_id) REFERENCES employees(id) ON DELETE SET NULL
        )
    """)

    # 13. Stock Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'Stock In', 'Stock Out', 'Transfer', 'Adjustment', 'Damage', 'Return', 'Replacement'
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL, -- YYYY-MM-DD
            time TEXT,
            user TEXT,
            reason TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES inventory(id) ON DELETE CASCADE
        )
    """)

    # 14. Investment Portfolio Table (For Market & Investments)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investment_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            type TEXT NOT NULL, -- 'Stock', 'Crypto', 'Mutual Fund', 'ETF'
            purchase_price REAL NOT NULL,
            quantity REAL NOT NULL,
            current_price REAL NOT NULL,
            date_purchased TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 15. Market Watchlist Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            ticker TEXT NOT NULL,
            type TEXT NOT NULL,
            current_price REAL NOT NULL,
            change_percentage REAL DEFAULT 0.0,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    # 16. Scheduled Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            report_type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            format TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    seed_data(conn)
    conn.close()

def seed_company_employees_and_payroll(conn, company_id, company_name):
    cursor = conn.cursor()
    domain = company_name.lower().replace(" ", "").replace("&", "") + ".com"
    if company_name == 'Nexus Corp':
        domain = 'nexus.com'
    elif company_name == 'Apex Systems':
        domain = 'apex.com'
        
    prefix = "".join([w[0] for w in company_name.split() if w.isalnum()]).upper()[:3]
    if len(prefix) < 2:
        prefix = company_name[:3].upper()

    # 1. Seed progressive tax slabs (progressivity)
    slabs_data = [
        (0.0, 300000.0, 0.00),
        (300000.0, 700000.0, 0.05),
        (700000.0, 1000000.0, 0.10),
        (1000000.0, 1500000.0, 0.15),
        (1500000.0, None, 0.20),
    ]
    for min_inc, max_inc, rate in slabs_data:
        cursor.execute("""
            INSERT INTO tax_slabs (company_id, min_income, max_income, tax_rate)
            VALUES (?, ?, ?, ?)
        """, (company_id, min_inc, max_inc, rate))

    # 2. Seed default employees (with extended profile information)
    employees_data = [
        (company_id, f"{prefix}001", f"{company_name} Admin", f"admin@{domain}", "9876543201", 1, "Executive", "Director", 160000.0, "2023-01-10", "Admin", "admin123", "Male", "Ramesh Sen", "Sita Sen", "1985-05-15", 41, "O+", "9876543299", 15.0, "Master of Business Administration", "ABCDE1234F", "123456789012", "998877665544", "HDFC0000001", "https://randomuser.me/api/portraits/men/1.jpg", "123 High Street", "Maharashtra", "Mumbai", "India", "400001"),
        (company_id, f"{prefix}002", "Sarah HR Manager", f"hr@{domain}", "9876543202", 0, "HR", "HR Manager", 78000.0, "2023-05-15", "HR Manager", "hr123", "Female", "David Miller", "Emma Miller", "1990-08-20", 35, "A-", "9876543298", 8.5, "Master of Human Resource Management", "FGHIJ5678K", "987654321098", "112233445566", "ICIC0000002", "https://randomuser.me/api/portraits/women/2.jpg", "456 HR Blvd", "Karnataka", "Bengaluru", "India", "560001"),
        (company_id, f"{prefix}101", "Vikram Sen", f"vikram@{domain}", "9876543203", 0, "IT", "Lead Architect", 120000.0, "2024-01-15", "Employee", "employee123", "Male", "Harish Sen", "Meera Sen", "1988-12-05", 37, "B+", "9876543297", 10.0, "B.Tech Computer Science", "LMNOP9012Q", "111122223333", "223344556677", "SBIN0000003", "https://randomuser.me/api/portraits/men/3.jpg", "789 Tech Road", "Delhi", "New Delhi", "India", "110001"),
        (company_id, f"{prefix}102", "Priya Sharma", f"priya@{domain}", "9876543204", 1, "IT", "Senior Engineer", 90000.0, "2024-09-01", "Employee", "employee123", "Female", "Anoop Sharma", "Kriti Sharma", "1993-04-10", 33, "AB+", "9876543296", 6.0, "M.Tech Software Engineering", "RSTUV3456W", "444455556666", "334455667788", "AXIS0000004", "https://randomuser.me/api/portraits/women/4.jpg", "101 Code Lane", "Uttar Pradesh", "Noida", "India", "201301"),
        (company_id, f"{prefix}103", "Rohan Das", f"rohan@{domain}", "9876543205", 0, "IT", "QA Analyst", 55000.0, "2025-01-10", "Employee", "employee123", "Male", "Suresh Das", "Gouri Das", "1996-07-22", 29, "O-", "9876543295", 3.0, "B.Sc Information Technology", "XYZAB7890C", "777788889999", "445566778899", "BARB0000005", "https://randomuser.me/api/portraits/men/5.jpg", "202 Test St", "West Bengal", "Kolkata", "India", "700001"),
        (company_id, f"{prefix}201", "Anjali Nair", f"anjali@{domain}", "9876543206", 1, "Finance", "Finance Manager", 80000.0, "2023-11-10", "Finance Manager", "employee123", "Female", "Balakrishnan Nair", "Radha Nair", "1991-03-30", 35, "B-", "9876543294", 7.0, "Chartered Accountant", "DEFGH1234I", "112211221122", "556677889900", "CNRB0000006", "https://randomuser.me/api/portraits/women/6.jpg", "303 Coin Crescent", "Kerala", "Kochi", "India", "682001"),
    ]

    for row in employees_data:
        cursor.execute("""
            INSERT INTO employees (
                company_id, employee_id_code, name, email, phone, phone_verified, department, designation, basic_salary, joining_date, role, password,
                gender, father_name, mother_name, dob, age, blood_group, emergency_contact, experience, education, pan_number, aadhaar_number, bank_account, ifsc_code, photo, address, state, city, country, pin_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    conn.commit()

    # Get employee IDs
    cursor.execute("SELECT id, basic_salary FROM employees WHERE company_id = ?", (company_id,))
    emps = cursor.fetchall()

    # 3. Generate historical payroll records (5 months)
    months = [2, 3, 4, 5, 6]
    for month in months:
        for emp in emps:
            emp_db_id = emp[0]
            basic = emp[1]
            
            hra = basic * 0.40
            da = basic * 0.10
            med = 1250.0
            travel = 1600.0
            bonus = basic * 0.10 if month == 3 else 0.0 # March appraisal bonus
            
            gross = basic + hra + da + med + travel + bonus
            pf = basic * 0.12
            pt = 200.0
            ins = 1000.0
            
            annual_gross = (basic + hra + da + med + travel) * 12 + bonus
            taxable_income = max(0.0, annual_gross - 75000.0)
            
            tax_amount = 0.0
            for min_s, max_s, rate in slabs_data:
                if taxable_income > min_s:
                    if max_s is None or taxable_income <= max_s:
                        tax_amount += (taxable_income - min_s) * rate
                        break
                    else:
                        tax_amount += (max_s - min_s) * rate

            monthly_tax = tax_amount / 12.0
            net = gross - pf - pt - monthly_tax - ins
            
            cursor.execute("""
                INSERT INTO payroll_records (
                    employee_id, month, year, basic_salary, hra, da, bonus, 
                    medical_allowance, travel_allowance, gross_salary, 
                    pf, professional_tax, income_tax, insurance, net_salary, 
                    working_days, paid_leaves, unpaid_leaves, processed_at
                ) VALUES (?, ?, 2026, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 26, 0, 0, ?)
            """, (
                emp_db_id, month, basic, hra, da, bonus, 
                med, travel, gross, 
                pf, pt, monthly_tax, ins, net,
                f"2026-0{month}-28 17:00:00"
            ))

    # 4. Seed Recruitment
    recruitment_data = [
        (company_id, "Devendra Kumar", "devendra@gmail.com", "9988776655", "Software Engineer", "Offer Letter", "Good technical skills in React & Python.", "2026-07-15", 1),
        (company_id, "Shikha Goel", "shikha@gmail.com", "9988776644", "HR Specialist", "Interviewing", "Strong screening capabilities.", "2026-07-22", 0),
        (company_id, "Abhinav Mishra", "abhinav@gmail.com", "9988776633", "Finance Analyst", "Applied", "Resume looks matching.", None, 0),
    ]
    for r in recruitment_data:
        cursor.execute("""
            INSERT INTO recruitment (company_id, candidate_name, email, phone, designation, status, feedback, interview_date, offer_letter_sent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, r)

    # 5. Seed Attendance
    for emp in emps:
        emp_db_id = emp[0]
        for day in range(1, 15):
            date_str = f"2026-07-{str(day).zfill(2)}"
            status = 'Present'
            clock_in = '09:05:00'
            clock_out = '18:10:00'
            late = 5
            overtime = 0.5 if day % 3 == 0 else 0.0
            
            if day == 5 or day == 12:
                status = 'Holiday'
                clock_in, clock_out, late, overtime = None, None, 0, 0.0
            elif day == 8:
                status = 'Absent'
                clock_in, clock_out, late, overtime = None, None, 0, 0.0

            cursor.execute("""
                INSERT OR IGNORE INTO attendance (employee_id, date, clock_in, clock_out, late_entry, overtime_hours, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (emp_db_id, date_str, clock_in, clock_out, late, overtime, status))

    # 6. Seed Finance records
    finance_data = [
        (company_id, "Income", "Revenue", 550000.0, "Monthly retainer payouts from Client A", "2026-06-15"),
        (company_id, "Income", "Revenue", 420000.0, "Project delivery billing Client B", "2026-06-28"),
        (company_id, "Expense", "Operational", 85000.0, "Office rent and electricity", "2026-06-05"),
        (company_id, "Expense", "Operational", 24000.0, "AWS cloud hosting costs", "2026-06-10"),
        (company_id, "Expense", "Tax Paid", 68000.0, "Quarterly GST and local taxes paid", "2026-06-25"),
        
        # July entries
        (company_id, "Income", "Revenue", 600000.0, "Billing Client C", "2026-07-10"),
        (company_id, "Expense", "Operational", 90000.0, "Office rent and electricity", "2026-07-05"),
        (company_id, "Expense", "Operational", 30000.0, "AWS Cloud hosting and tool subscriptions", "2026-07-12"),
    ]
    for f in finance_data:
        cursor.execute("""
            INSERT INTO finance (company_id, type, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, f)

    # 7. Seed Department Budgets
    budgets_data = [
        (company_id, "IT", 150000.0, 7, 2026),
        (company_id, "HR", 40000.0, 7, 2026),
        (company_id, "Finance", 30000.0, 7, 2026),
    ]
    for b in budgets_data:
        cursor.execute("""
            INSERT OR IGNORE INTO department_budgets (company_id, department, budget, month, year)
            VALUES (?, ?, ?, ?, ?)
        """, b)

    # 8. Seed Suppliers
    suppliers_data = [
        (company_id, "TechSource Solutions", "TechSource Corp", "GSTIN27AABCT882", "9988776655", "sales@techsource.com", "789 tech Park, Mumbai", "Net 30", 5000.0),
        (company_id, "OfficeComforts Inc", "OfficeComforts Pvt Ltd", "GSTIN27FFDDS331", "9988776644", "support@officecomforts.com", "101 Comfort zone, Bengaluru", "COD", 0.0),
    ]
    for s in suppliers_data:
        cursor.execute("""
            INSERT INTO suppliers (company_id, supplier_name, company, gst_number, phone, email, address, payment_terms, outstanding_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, s)

    # Get supplier ID
    cursor.execute("SELECT id FROM suppliers WHERE company_id = ? LIMIT 1", (company_id,))
    sup_id = cursor.fetchone()[0]

    # 9. Seed Inventory (Assets)
    inventory_data = [
        (company_id, "ThinkPad L14 Gen 4", "SKU-LPT-001", "8827389101", "Laptops", "Lenovo", "ThinkPad L14", "SN-LN-87289", "Corporate dev laptops", "2025-01-10", 65000.0, 0.0, 18.0, sup_id, "Warehouse A", "Rack 1", 5, 2, 10, "Assigned", "2028-01-10", emps[2][0]),
        (company_id, "ThinkPad L14 Gen 4", "SKU-LPT-001", "8827389101", "Laptops", "Lenovo", "ThinkPad L14", "SN-LN-87290", "Corporate dev laptops", "2025-01-10", 65000.0, 0.0, 18.0, sup_id, "Warehouse A", "Rack 1", 5, 2, 10, "Assigned", "2028-01-10", emps[3][0]),
        (company_id, "Dell UltraSharp 24 Monitor", "SKU-MON-001", "8827389102", "Accessories", "Dell", "U2422H", "SN-DL-11002", "High resolution HR monitor", "2025-03-12", 18500.0, 0.0, 18.0, sup_id, "Warehouse A", "Rack 3", 10, 3, 20, "Available", "2027-03-12", None),
        (company_id, "Ergonomic Office Chair", "SKU-FUR-001", "8827389103", "Furniture", "Featherlite", "Liberate", "SN-FL-99120", "Executive seating", "2024-06-20", 12000.0, 0.0, 18.0, sup_id, "Warehouse A", "Floor 1", 15, 5, 30, "Available", "2029-06-20", None),
    ]
    for inv in inventory_data:
        cursor.execute("""
            INSERT INTO inventory (
                company_id, product_name, sku_code, barcode, category, brand, model, serial_number, description,
                purchase_date, purchase_price, selling_price, gst, supplier_id, warehouse, location, current_stock, minimum_stock, maximum_stock, status, warranty_expiry, assigned_employee_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, inv)

    # 10. Seed Market Watchlist
    watchlist_data = [
        (company_id, "Tata Consultancy Services", "TCS", "Stock", 4120.50, 1.25),
        (company_id, "Infosys Ltd", "INFY", "Stock", 1625.30, -0.45),
        (company_id, "Wipro Ltd", "WIPRO", "Stock", 485.60, 0.85),
        (company_id, "Bitcoin USD", "BTC-USD", "Crypto", 5430000.00, 3.45),
        (company_id, "Nifty 50 ETF", "NIFTYBEES", "ETF", 270.40, 0.12),
    ]
    for w in watchlist_data:
        cursor.execute("""
            INSERT INTO market_watchlist (company_id, name, ticker, type, current_price, change_percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, w)

    # 11. Seed Investment Portfolio
    portfolio_data = [
        (company_id, "Tata Consultancy Services", "TCS", "Stock", 3850.00, 150.0, 4120.50, "2025-11-20"),
        (company_id, "Bitcoin USD", "BTC-USD", "Crypto", 4800000.00, 0.5, 5430000.00, "2026-02-15"),
    ]
    for p in portfolio_data:
        cursor.execute("""
            INSERT INTO investment_portfolio (company_id, name, ticker, type, purchase_price, quantity, current_price, date_purchased)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    # Add audit log
    cursor.execute("""
        INSERT INTO audit_logs (company_id, user_email, action, details)
        VALUES (?, 'System', 'Workspace Setup', ?)
    """, (company_id, f"Workspace setup with default employees, recruitment, attendance, stock inventory, and investments portfolio for {company_name}."))
    
    conn.commit()

def seed_data(conn):
    cursor = conn.cursor()

    # Check if companies exist
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] > 0:
        return

    print("Seeding initial data...")

    # Seed default Nexus Corp and Apex Systems
    cursor.execute("INSERT INTO companies (name) VALUES ('Nexus Corp')")
    nexus_id = cursor.lastrowid
    seed_company_employees_and_payroll(conn, nexus_id, 'Nexus Corp')

    cursor.execute("INSERT INTO companies (name) VALUES ('Apex Systems')")
    apex_id = cursor.lastrowid
    seed_company_employees_and_payroll(conn, apex_id, 'Apex Systems')

    conn.commit()
    print("Database seeding completed.")

class PayrollDB:
    def __init__(self, db_file="payroll.db"):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Create GUI specific tables to prevent schema conflicts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gui_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT,
                pay_type TEXT NOT NULL,
                rate REAL NOT NULL,
                hours REAL DEFAULT 0.0,
                month TEXT NOT NULL,
                gross REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gui_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gui_revenue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_employee(self, name, position, pay_type, rate, hours, month):
        cursor = self.conn.cursor()
        gross = rate if pay_type == "Salary" else rate * hours
        cursor.execute("""
            INSERT INTO gui_employees (name, position, pay_type, rate, hours, month, gross)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, position, pay_type, rate, hours, month, gross))
        self.conn.commit()

    def get_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, position, pay_type, rate, hours, month, gross FROM gui_employees")
        return [tuple(row) for row in cursor.fetchall()]

    def delete_employee(self, emp_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM gui_employees WHERE id = ?", (emp_id,))
        self.conn.commit()

    def add_expense(self, category, description, amount, date_str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO gui_expenses (category, description, amount, date)
            VALUES (?, ?, ?, ?)
        """, (category, description, amount, date_str))
        self.conn.commit()

    def get_expenses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, category, description, amount, date FROM gui_expenses")
        return [tuple(row) for row in cursor.fetchall()]

    def delete_expense(self, exp_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM gui_expenses WHERE id = ?", (exp_id,))
        self.conn.commit()

    def add_revenue(self, source, amount, date_str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO gui_revenue (source, amount, date)
            VALUES (?, ?, ?)
        """, (source, amount, date_str))
        self.conn.commit()

    def get_revenue(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, source, amount, date FROM gui_revenue")
        return [tuple(row) for row in cursor.fetchall()]

    def delete_revenue(self, rev_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM gui_revenue WHERE id = ?", (rev_id,))
        self.conn.commit()

    def get_available_months(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT month FROM gui_employees
            UNION
            SELECT DISTINCT substr(date, 1, 7) FROM gui_expenses
            UNION
            SELECT DISTINCT substr(date, 1, 7) FROM gui_revenue
            ORDER BY month DESC
        """)
        return [row[0] for row in cursor.fetchall() if row[0]]

    def get_total_revenue(self, month=None):
        cursor = self.conn.cursor()
        if month:
            cursor.execute("SELECT SUM(amount) FROM gui_revenue WHERE substr(date, 1, 7) = ?", (month,))
        else:
            cursor.execute("SELECT SUM(amount) FROM gui_revenue")
        res = cursor.fetchone()[0]
        return res if res else 0.0

    def get_total_wages(self, month=None):
        cursor = self.conn.cursor()
        if month:
            cursor.execute("SELECT SUM(gross) FROM gui_employees WHERE month = ?", (month,))
        else:
            cursor.execute("SELECT SUM(gross) FROM gui_employees")
        res = cursor.fetchone()[0]
        return res if res else 0.0

    def get_total_expenses(self, month=None):
        cursor = self.conn.cursor()
        if month:
            cursor.execute("SELECT SUM(amount) FROM gui_expenses WHERE substr(date, 1, 7) = ?", (month,))
        else:
            cursor.execute("SELECT SUM(amount) FROM gui_expenses")
        res = cursor.fetchone()[0]
        return res if res else 0.0

    def get_expense_breakdown(self, month=None):
        cursor = self.conn.cursor()
        if month:
            cursor.execute("""
                SELECT category, SUM(amount) 
                FROM gui_expenses 
                WHERE substr(date, 1, 7) = ? 
                GROUP BY category
            """, (month,))
        else:
            cursor.execute("SELECT category, SUM(amount) FROM gui_expenses GROUP BY category")
        return [tuple(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    init_db()
