import os
import io
import re
import sqlite3
import random
import datetime
from flask import Flask, request, jsonify, session, render_template, send_file
from database import init_db, get_db_connection, DATABASE_FILE
from salary_engine import calculate_payroll_details
from report_engine import generate_csv_report, generate_excel_report, generate_pdf_report, simulate_email_report, num_to_words


app = Flask(__name__)
app.secret_key = "payroll_secret_key_for_session_management_12345"

# Initialize database on startup
if not os.path.exists(DATABASE_FILE):
    init_db()
else:
    init_db()

# Log Helper
def write_audit_log(company_id, user_email, action, details=""):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (company_id, user_email, action, details)
            VALUES (?, ?, ?, ?)
        """, (company_id, user_email, action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error writing audit log: {e}")

# Role Helper
def is_admin_or_manager(role):
    return role in ['Admin', 'Super Admin', 'HR Manager', 'Finance Manager', 'Payroll Manager']

# Helper for counting unpaid leaves
def count_unpaid_leaves_in_month(employee_id, month, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT start_date, end_date FROM leave_requests
        WHERE employee_id = ? AND status = 'Approved' AND leave_type = 'Unpaid'
    """, (employee_id,))
    rows = cursor.fetchall()
    conn.close()
    
    count = 0
    for row in rows:
        try:
            start = datetime.datetime.strptime(row['start_date'], "%Y-%m-%d").date()
            end = datetime.datetime.strptime(row['end_date'], "%Y-%m-%d").date()
            
            curr = start
            while curr <= end:
                if curr.month == month and curr.year == year:
                    count += 1
                curr += datetime.timedelta(days=1)
        except Exception as e:
            print(f"Error parsing date in leave calculation: {e}")
    return count


# --- FRONTEND ROUTE ---
@app.route("/")
def index():
    return render_template("index.html")


# --- Email Validation Helper ---
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email):
    """Validate email format using regex."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


# --- AUTH APIs ---

@app.route("/api/auth/companies", methods=["GET"])
def list_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies ORDER BY name")
    companies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(companies)

@app.route("/api/auth/companies", methods=["POST"])
def add_company():
    data = request.get_json() or {}
    name = data.get("name")
    if not name or not name.strip():
        return jsonify({"error": "Company name is required"}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO companies (name) VALUES (?)", (name.strip(),))
        company_id = cursor.lastrowid
        
        from database import seed_company_employees_and_payroll
        seed_company_employees_and_payroll(conn, company_id, name.strip())
        
        conn.commit()
        write_audit_log(company_id, "System", "Create Company", f"Company '{name}' registered and fully seeded.")
        return jsonify({"id": company_id, "name": name})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Company name already exists"}), 400
    finally:
        conn.close()

@app.route("/api/auth/credentials", methods=["GET"])
def get_demo_credentials():
    company_id = request.args.get("company_id")
    if not company_id:
        return jsonify({"error": "company_id is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, password, role, name 
        FROM employees 
        WHERE company_id = ? AND status = 'Active'
        ORDER BY id ASC
        LIMIT 10
    """, (company_id,))
    creds = [{"email": row["email"], "password": row["password"], "role": row["role"], "name": row["name"]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(creds)

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    phone = data.get("phone", "").strip()
    company_id = data.get("company_id")
    captcha_val = data.get("captcha")
    
    if not name or not email or not password or not company_id:
        return jsonify({"error": "Name, email, password, and company are required"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format. Please use a valid email like name@gmail.com"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
        
    is_testing = app.config.get("TESTING", False)
    expected_captcha = session.get("captcha_answer")
    if not is_testing and (not expected_captcha or str(captcha_val).strip() != str(expected_captcha)):
        return jsonify({"error": "Incorrect CAPTCHA answer"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM companies WHERE id = ?", (company_id,))
    company = cursor.fetchone()
    if not company:
        conn.close()
        return jsonify({"error": "Selected company does not exist"}), 404
    
    prefix = "".join([w[0] for w in company["name"].split() if w.isalnum()]).upper()[:3]
    if len(prefix) < 2:
        prefix = company["name"][:3].upper()
    cursor.execute("SELECT COUNT(*) FROM employees WHERE company_id = ?", (company_id,))
    count = cursor.fetchone()[0]
    emp_code = f"{prefix}{str(count + 1).zfill(3)}"
    
    try:
        cursor.execute("""
            INSERT INTO employees (company_id, employee_id_code, name, email, phone, department, designation, basic_salary, joining_date, role, password)
            VALUES (?, ?, ?, ?, ?, 'General', 'Employee', 50000.0, date('now'), 'Employee', ?)
        """, (company_id, emp_code, name, email, phone, password))
        new_id = cursor.lastrowid
        conn.commit()
        
        session.pop("captcha_answer", None)
        
        session["user"] = {
            "id": new_id,
            "name": name,
            "email": email,
            "role": "Employee",
            "company_id": int(company_id)
        }
        
        write_audit_log(int(company_id), email, "Signup", f"New user {name} registered with email {email}")
        
        return jsonify({
            "id": new_id,
            "name": name,
            "email": email,
            "role": "Employee",
            "company_id": int(company_id),
            "message": "Account created successfully! You are now logged in."
        })
    except sqlite3.IntegrityError:
        return jsonify({"error": "This email is already registered in this company. Please login instead."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/auth/captcha", methods=["GET"])
def get_captcha():
    num1 = random.randint(1, 15)
    num2 = random.randint(1, 15)
    operation = random.choice(["+", "-"])
    if operation == "+":
        answer = num1 + num2
    else:
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        
    question = f"{num1} {operation} {num2}"
    session["captcha_answer"] = str(answer)
    return jsonify({"question": question})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password")
    company_id = data.get("company_id")
    captcha_val = data.get("captcha")
    
    if not email or not password or not company_id or captcha_val is None:
        return jsonify({"error": "Email, password, company, and CAPTCHA are required"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format. Please use a valid email like name@gmail.com"}), 400
        
    is_testing = app.config.get("TESTING", False)
    expected_captcha = session.get("captcha_answer")
    if not is_testing and (not expected_captcha or str(captcha_val).strip() != expected_captcha):
        return jsonify({"error": "Incorrect CAPTCHA answer"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, role, password, status, phone_verified 
        FROM employees 
        WHERE email = ? AND company_id = ?
    """, (email, company_id))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid email, password, or company"}), 401
        
    if user["status"] == "Inactive":
        return jsonify({"error": "Your account has been deactivated. Please contact Admin."}), 403
        
    session["user"] = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "company_id": int(company_id),
        "phone_verified": user["phone_verified"]
    }
    
    session.pop("captcha_answer", None)
    write_audit_log(int(company_id), email, "Login Success", f"Logged in directly as {user['role']}")
    
    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "company_id": int(company_id),
        "phone_verified": user["phone_verified"]
    })

@app.route("/api/auth/verify_otp", methods=["POST"])
def verify_otp():
    if "user" in session:
        return jsonify(session["user"])
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/api/employees/verify-phone-init", methods=["POST"])
def verify_phone_init():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400
        
    code = str(random.randint(100000, 999999))
    session["phone_verification"] = {
        "phone": phone,
        "code": code
    }
    
    return jsonify({
        "success": True,
        "message": "Simulated SMS verification code sent",
        "code_simulated": code
    })

@app.route("/api/employees/verify-phone-confirm", methods=["POST"])
def verify_phone_confirm():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    code_entered = data.get("code")
    
    verification = session.get("phone_verification")
    if not verification:
        return jsonify({"error": "No verification request pending"}), 400
        
    if verification["code"] != str(code_entered).strip():
        return jsonify({"error": "Invalid verification code"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees 
        SET phone = ?, phone_verified = 1
        WHERE id = ? AND company_id = ?
    """, (verification["phone"], user["id"], user["company_id"]))
    conn.commit()
    conn.close()
    
    session.pop("phone_verification", None)
    session["user"]["phone_verified"] = 1
    session.modified = True
    
    write_audit_log(user["company_id"], user["email"], "Verify Phone", f"Verified phone number {verification['phone']}.")
    return jsonify({"success": True, "message": "Phone number successfully verified!"})

@app.route("/api/auth/session", methods=["GET"])
def check_session():
    if "user" in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT phone_verified FROM employees WHERE id = ?", (session["user"]["id"],))
        row = cursor.fetchone()
        conn.close()
        if row:
            session["user"]["phone_verified"] = row["phone_verified"]
        return jsonify({"authenticated": True, "user": session["user"]})
    return jsonify({"authenticated": False})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    if "user" in session:
        user = session["user"]
        write_audit_log(user["company_id"], user["email"], "Logout", "Logged out successfully")
        session.pop("user", None)
    return jsonify({"message": "Logged out successfully"})


# --- EMPLOYEES CRUD APIs ---

@app.route("/api/employees", methods=["GET"])
def get_employees():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_admin_or_manager(user["role"]):
        cursor.execute("""
            SELECT * FROM employees 
            WHERE company_id = ? 
            ORDER BY employee_id_code
        """, (user["company_id"],))
        emps = [dict(row) for row in cursor.fetchall()]
    else:
        cursor.execute("""
            SELECT * FROM employees 
            WHERE id = ? AND company_id = ?
        """, (user["id"], user["company_id"]))
        emps = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return jsonify(emps)

@app.route("/api/employees", methods=["POST"])
def add_employee():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    emp_code = data.get("employee_id_code")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    dept = data.get("department")
    desig = data.get("designation")
    basic_salary = data.get("basic_salary")
    joining_date = data.get("joining_date")
    role = data.get("role", "Employee")
    password = data.get("password", "employee123")
    
    gender = data.get("gender", "Male")
    father_name = data.get("father_name", "")
    mother_name = data.get("mother_name", "")
    dob = data.get("dob", "")
    age = data.get("age", 25)
    blood_group = data.get("blood_group", "O+")
    emergency_contact = data.get("emergency_contact", "")
    experience = data.get("experience", 0.0)
    education = data.get("education", "")
    pan_number = data.get("pan_number", "")
    aadhaar_number = data.get("aadhaar_number", "")
    bank_account = data.get("bank_account", "")
    ifsc_code = data.get("ifsc_code", "")
    photo = data.get("photo", "")
    address = data.get("address", "")
    state = data.get("state", "")
    city = data.get("city", "")
    country = data.get("country", "")
    pin_code = data.get("pin_code", "")
    
    if not all([emp_code, name, email, dept, desig, basic_salary, joining_date]):
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO employees (
                company_id, employee_id_code, name, email, phone, department, designation, basic_salary, joining_date, role, password,
                gender, father_name, mother_name, dob, age, blood_group, emergency_contact, experience, education, pan_number, aadhaar_number, bank_account, ifsc_code, photo, address, state, city, country, pin_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["company_id"], emp_code, name, email, phone, dept, desig, float(basic_salary), joining_date, role, password,
            gender, father_name, mother_name, dob, age, blood_group, emergency_contact, experience, education, pan_number, aadhaar_number, bank_account, ifsc_code, photo, address, state, city, country, pin_code
        ))
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Add Employee", f"Added {name} ({emp_code})")
        return jsonify({"message": "Employee added successfully", "id": cursor.lastrowid})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Employee Code or Email already exists in this company"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/employees/<int:emp_id>", methods=["PUT"])
def update_employee(emp_id):
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    dept = data.get("department")
    desig = data.get("designation")
    basic_salary = data.get("basic_salary")
    joining_date = data.get("joining_date")
    role = data.get("role")
    status = data.get("status")
    password = data.get("password")
    
    gender = data.get("gender")
    father_name = data.get("father_name")
    mother_name = data.get("mother_name")
    dob = data.get("dob")
    age = data.get("age")
    blood_group = data.get("blood_group")
    emergency_contact = data.get("emergency_contact")
    experience = data.get("experience")
    education = data.get("education")
    pan_number = data.get("pan_number")
    aadhaar_number = data.get("aadhaar_number")
    bank_account = data.get("bank_account")
    ifsc_code = data.get("ifsc_code")
    photo = data.get("photo")
    address = data.get("address")
    state = data.get("state")
    city = data.get("city")
    country = data.get("country")
    pin_code = data.get("pin_code")
    
    if not all([name, email, dept, desig, basic_salary, joining_date]):
        return jsonify({"error": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM employees WHERE id = ? AND company_id = ?", (emp_id, user["company_id"]))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Employee not found"}), 404
        
    try:
        query = """
            UPDATE employees 
            SET name = ?, email = ?, phone = ?, department = ?, designation = ?, basic_salary = ?, joining_date = ?, role = ?, status = ?,
                gender = ?, father_name = ?, mother_name = ?, dob = ?, age = ?, blood_group = ?, emergency_contact = ?, experience = ?, education = ?, 
                pan_number = ?, aadhaar_number = ?, bank_account = ?, ifsc_code = ?, photo = ?, address = ?, state = ?, city = ?, country = ?, pin_code = ?
        """
        params = [
            name, email, phone, dept, desig, float(basic_salary), joining_date, role, status,
            gender, father_name, mother_name, dob, age, blood_group, emergency_contact, experience, education,
            pan_number, aadhaar_number, bank_account, ifsc_code, photo, address, state, city, country, pin_code
        ]
        
        if password and password.strip():
            query += ", password = ?"
            params.append(password)
            
        query += " WHERE id = ? AND company_id = ?"
        params.extend([emp_id, user["company_id"]])
        
        cursor.execute(query, tuple(params))
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Update Employee", f"Updated details for employee ID {emp_id}")
        return jsonify({"message": "Employee updated successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists in this company"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/employees/<int:emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if emp_id == user["id"]:
        conn.close()
        return jsonify({"error": "Cannot delete your own admin account"}), 400
        
    cursor.execute("SELECT name FROM employees WHERE id = ? AND company_id = ?", (emp_id, user["company_id"]))
    emp = cursor.fetchone()
    if not emp:
        conn.close()
        return jsonify({"error": "Employee not found"}), 404
        
    cursor.execute("DELETE FROM employees WHERE id = ? AND company_id = ?", (emp_id, user["company_id"]))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Delete Employee", f"Deleted employee {emp['name']} (ID {emp_id})")
    return jsonify({"message": "Employee deleted successfully"})


# --- TAX SLABS APIs ---

@app.route("/api/tax_slabs", methods=["GET"])
def get_tax_slabs():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, min_income, max_income, tax_rate 
        FROM tax_slabs 
        WHERE company_id = ? 
        ORDER BY min_income
    """, (user["company_id"],))
    slabs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(slabs)

@app.route("/api/tax_slabs", methods=["PUT"])
def update_tax_slabs():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    slabs_list = request.get_json() or []
    if not isinstance(slabs_list, list):
        return jsonify({"error": "Invalid format, must be a list"}), 400
        
    for slab in slabs_list:
        min_i = slab.get("min_income")
        rate = slab.get("tax_rate")
        if min_i is None or rate is None:
            return jsonify({"error": "Min Income and Tax Rate are required for all slabs"}), 400
            
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM tax_slabs WHERE company_id = ?", (user["company_id"],))
        for slab in slabs_list:
            min_i = float(slab["min_income"])
            max_i = float(slab["max_income"]) if slab.get("max_income") is not None else None
            rate = float(slab["tax_rate"])
            
            cursor.execute("""
                INSERT INTO tax_slabs (company_id, min_income, max_income, tax_rate)
                VALUES (?, ?, ?, ?)
            """, (user["company_id"], min_i, max_i, rate))
            
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Update Tax Slabs", "Updated progressive tax slab brackets")
        return jsonify({"message": "Tax slabs updated successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --- LEAVE REQUESTS APIs ---

@app.route("/api/leave_requests", methods=["GET"])
def get_leave_requests():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_admin_or_manager(user["role"]):
        cursor.execute("""
            SELECT l.id, l.employee_id, e.name as employee_name, e.employee_id_code, 
                   l.start_date, l.end_date, l.leave_type, l.reason, l.status, l.created_at
            FROM leave_requests l
            JOIN employees e ON l.employee_id = e.id
            WHERE e.company_id = ?
            ORDER BY l.created_at DESC
        """, (user["company_id"],))
    else:
        cursor.execute("""
            SELECT id, employee_id, start_date, end_date, leave_type, reason, status, created_at
            FROM leave_requests
            WHERE employee_id = ?
            ORDER BY created_at DESC
        """, (user["id"],))
        
    leaves = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(leaves)

@app.route("/api/leave_requests", methods=["POST"])
def create_leave_request():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    leave_type = data.get("leave_type") 
    reason = data.get("reason")
    
    if not all([start_date, end_date, leave_type]):
        return jsonify({"error": "Start date, end date, and leave type are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leave_requests (employee_id, start_date, end_date, leave_type, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (user["id"], start_date, end_date, leave_type, reason))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Request Leave", f"Applied for {leave_type} leave ({start_date} to {end_date})")
    return jsonify({"message": "Leave request submitted successfully"})

@app.route("/api/leave_requests/<int:leave_id>", methods=["PUT"])
def update_leave_status(leave_id):
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    status = data.get("status") 
    
    if status not in ["Approved", "Rejected"]:
        return jsonify({"error": "Invalid status"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.id, e.name, l.leave_type, l.start_date, l.end_date
        FROM leave_requests l
        JOIN employees e ON l.employee_id = e.id
        WHERE l.id = ? AND e.company_id = ?
    """, (leave_id, user["company_id"]))
    leave = cursor.fetchone()
    if not leave:
        conn.close()
        return jsonify({"error": "Leave request not found"}), 404
        
    cursor.execute("UPDATE leave_requests SET status = ? WHERE id = ?", (status, leave_id))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Update Leave", f"Marked leave for {leave['name']} as {status} (Type: {leave['leave_type']})")
    return jsonify({"message": f"Leave request {status.lower()} successfully"})


# --- PAYROLL APIs ---

@app.route("/api/payroll", methods=["GET"])
def get_payroll_records():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    month = request.args.get("month")
    year = request.args.get("year")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_admin_or_manager(user["role"]):
        query = """
            SELECT p.*, e.name as employee_name, e.employee_id_code, e.department, e.designation
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            WHERE e.company_id = ?
        """
        params = [user["company_id"]]
        if month:
            query += " AND p.month = ?"
            params.append(int(month))
        if year:
            query += " AND p.year = ?"
            params.append(int(year))
        query += " ORDER BY e.employee_id_code, p.year DESC, p.month DESC"
        cursor.execute(query, tuple(params))
    else:
        query = """
            SELECT p.*, e.name as employee_name, e.employee_id_code, e.department, e.designation
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            WHERE p.employee_id = ? AND e.company_id = ?
        """
        params = [user["id"], user["company_id"]]
        if month:
            query += " AND p.month = ?"
            params.append(int(month))
        if year:
            query += " AND p.year = ?"
            params.append(int(year))
        query += " ORDER BY p.year DESC, p.month DESC"
        cursor.execute(query, tuple(params))
        
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(records)

@app.route("/api/payroll/generate", methods=["POST"])
def generate_payroll():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    month = data.get("month")
    year = data.get("year")
    employee_ids = data.get("employee_ids") 
    custom_working_days = data.get("working_days", 26)
    
    bonus_override = data.get("bonus", 0.0)
    unpaid_leaves_override = data.get("unpaid_leaves") 
    
    if not month or not year:
        return jsonify({"error": "Month and Year are required"}), 400
        
    month = int(month)
    year = int(year)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT min_income, max_income, tax_rate 
        FROM tax_slabs 
        WHERE company_id = ?
    """, (user["company_id"],))
    tax_slabs = [dict(row) for row in cursor.fetchall()]
    
    if employee_ids:
        placeholders = ",".join("?" for _ in employee_ids)
        cursor.execute(f"""
            SELECT id, name, basic_salary, status 
            FROM employees 
            WHERE id IN ({placeholders}) AND company_id = ? AND status = 'Active'
        """, tuple(employee_ids) + (user["company_id"],))
    else:
        cursor.execute("""
            SELECT id, name, basic_salary, status 
            FROM employees 
            WHERE company_id = ? AND status = 'Active' AND role != 'Admin'
        """, (user["company_id"],))
        
    employees = cursor.fetchall()
    
    if not employees:
        conn.close()
        return jsonify({"error": "No active employees found to process"}), 404
        
    processed_count = 0
    errors = []
    
    for emp in employees:
        emp_id = emp["id"]
        emp_name = emp["name"]
        basic_sal = emp["basic_salary"]
        
        if employee_ids and len(employee_ids) == 1 and unpaid_leaves_override is not None:
            unpaid_leaves = int(unpaid_leaves_override)
        else:
            unpaid_leaves = count_unpaid_leaves_in_month(emp_id, month, year)
            
        bonus = float(bonus_override) if (employee_ids and len(employee_ids) == 1) else 0.0
        
        calc = calculate_payroll_details(
            basic_salary=basic_sal,
            bonus=bonus,
            working_days=int(custom_working_days),
            unpaid_leaves=unpaid_leaves,
            tax_slabs=tax_slabs
        )
        
        try:
            cursor.execute("""
                INSERT INTO payroll_records (
                    employee_id, month, year, basic_salary, hra, da, bonus, 
                    medical_allowance, travel_allowance, gross_salary, 
                    pf, professional_tax, income_tax, insurance, net_salary, 
                    working_days, paid_leaves, unpaid_leaves
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                ON CONFLICT(employee_id, month, year) DO UPDATE SET
                    basic_salary=excluded.basic_salary,
                    hra=excluded.hra,
                    da=excluded.da,
                    bonus=excluded.bonus,
                    medical_allowance=excluded.medical_allowance,
                    travel_allowance=excluded.travel_allowance,
                    gross_salary=excluded.gross_salary,
                    pf=excluded.pf,
                    professional_tax=excluded.professional_tax,
                    income_tax=excluded.income_tax,
                    insurance=excluded.insurance,
                    net_salary=excluded.net_salary,
                    working_days=excluded.working_days,
                    unpaid_leaves=excluded.unpaid_leaves,
                    processed_at=CURRENT_TIMESTAMP
            """, (
                emp_id, month, year, calc["basic_salary"], calc["hra"], calc["da"], calc["bonus"],
                calc["medical_allowance"], calc["travel_allowance"], calc["gross_salary"],
                calc["pf"], calc["professional_tax"], calc["income_tax"], calc["insurance"], calc["net_salary"],
                calc["working_days"], calc["unpaid_leaves"]
            ))
            processed_count += 1
        except Exception as e:
            errors.append(f"Error processing {emp_name}: {str(e)}")
            
    conn.commit()
    conn.close()
    
    details_str = f"Generated payroll for {processed_count} employees for {month}/{year}."
    if errors:
        details_str += f" Errors: {len(errors)}"
    write_audit_log(user["company_id"], user["email"], "Generate Payroll", details_str)
    
    return jsonify({
        "success": True,
        "processed_count": processed_count,
        "errors": errors
    })


# --- AUDIT LOGS API ---

@app.route("/api/audit_logs", methods=["GET"])
def get_audit_logs():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_email, action, details, timestamp 
        FROM audit_logs 
        WHERE company_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 100
    """, (user["company_id"],))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(logs)


# --- PERSISTENCE: DB BACKUP & RESTORE API ---

@app.route("/api/backup", methods=["GET"])
def download_backup():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    write_audit_log(user["company_id"], user["email"], "Backup Database", "Downloaded SQLite database backup file.")
    
    if os.path.exists(DATABASE_FILE):
        return send_file(
            DATABASE_FILE,
            as_attachment=True,
            download_name=f"payroll_backup_{datetime.date.today()}.db",
            mimetype="application/x-sqlite3"
        )
    return jsonify({"error": "Database file not found"}), 404

@app.route("/api/backup/restore", methods=["POST"])
def restore_backup():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    write_audit_log(user["company_id"], user["email"], "Restore Database", "Triggered database restore simulation.")
    return jsonify({"success": True, "message": "Database restore completed successfully (Simulated)."})


# --- HR RECRUITMENT APIs ---

@app.route("/api/hr/recruitment", methods=["GET"])
def get_recruitment():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recruitment WHERE company_id = ? ORDER BY created_at DESC", (user["company_id"],))
    applicants = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(applicants)

@app.route("/api/hr/recruitment", methods=["POST"])
def add_recruitment():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    name = data.get("candidate_name")
    email = data.get("email")
    phone = data.get("phone")
    desig = data.get("designation")
    
    if not name or not email or not desig:
        return jsonify({"error": "Candidate name, email, and designation are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recruitment (company_id, candidate_name, email, phone, designation, status)
        VALUES (?, ?, ?, ?, ?, 'Applied')
    """, (user["company_id"], name, email, phone, desig))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Add Applicant", f"Added applicant {name} for {desig}")
    return jsonify({"success": True, "message": "Applicant added successfully"})

@app.route("/api/hr/recruitment/<int:cand_id>", methods=["PUT"])
def update_recruitment(cand_id):
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    status = data.get("status")
    feedback = data.get("feedback")
    interview_date = data.get("interview_date")
    offer_letter_sent = data.get("offer_letter_sent", 0)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recruitment
        SET status = ?, feedback = ?, interview_date = ?, offer_letter_sent = ?
        WHERE id = ? AND company_id = ?
    """, (status, feedback, interview_date, offer_letter_sent, cand_id, user["company_id"]))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Update Applicant", f"Updated applicant ID {cand_id} to status {status}")
    return jsonify({"success": True, "message": "Applicant updated successfully"})


# --- ATTENDANCE APIs ---

@app.route("/api/attendance", methods=["GET"])
def get_attendance():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if is_admin_or_manager(user["role"]):
        cursor.execute("""
            SELECT a.*, e.name as employee_name, e.employee_id_code, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE e.company_id = ?
            ORDER BY a.date DESC
        """, (user["company_id"],))
    else:
        cursor.execute("""
            SELECT a.*, e.name as employee_name, e.employee_id_code, e.department
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE a.employee_id = ? AND e.company_id = ?
            ORDER BY a.date DESC
        """, (user["id"], user["company_id"]))
        
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(records)

@app.route("/api/attendance/clock_in", methods=["POST"])
def attendance_clock_in():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now_time = datetime.datetime.now().time()
    threshold = datetime.time(9, 0, 0)
    late_minutes = 0
    if now_time > threshold:
        late_minutes = (datetime.datetime.combine(datetime.date.today(), now_time) - 
                        datetime.datetime.combine(datetime.date.today(), threshold)).seconds // 60
                        
    try:
        cursor.execute("""
            INSERT INTO attendance (employee_id, date, clock_in, status, late_entry)
            VALUES (?, ?, ?, 'Present', ?)
            ON CONFLICT(employee_id, date) DO UPDATE SET
                clock_in = COALESCE(clock_in, excluded.clock_in),
                status = 'Present'
        """, (user["id"], today_str, now_str, late_minutes))
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Clock In", f"Clocked in at {now_str} (Late: {late_minutes} min)")
        return jsonify({"success": True, "message": "Clocked in successfully!", "time": now_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/attendance/clock_out", methods=["POST"])
def attendance_clock_out():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now_time = datetime.datetime.now().time()
    threshold_out = datetime.time(18, 0, 0)
    overtime_hours = 0.0
    if now_time > threshold_out:
        overtime_hours = round((datetime.datetime.combine(datetime.date.today(), now_time) - 
                               datetime.datetime.combine(datetime.date.today(), threshold_out)).seconds / 3600.0, 2)
                               
    try:
        cursor.execute("""
            UPDATE attendance 
            SET clock_out = ?, overtime_hours = ?
            WHERE employee_id = ? AND date = ?
        """, (now_str, overtime_hours, user["id"], today_str))
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Clock Out", f"Clocked out at {now_str} (Overtime: {overtime_hours} hrs)")
        return jsonify({"success": True, "message": "Clocked out successfully!", "time": now_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/attendance/log", methods=["POST"])
def attendance_log_custom():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    emp_id = data.get("employee_id")
    date_val = data.get("date")
    status = data.get("status")
    clock_in = data.get("clock_in")
    clock_out = data.get("clock_out")
    late = data.get("late_entry", 0)
    overtime = data.get("overtime_hours", 0.0)
    
    if not emp_id or not date_val or not status:
        return jsonify({"error": "Employee ID, Date, and Status are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attendance (employee_id, date, clock_in, clock_out, late_entry, overtime_hours, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(employee_id, date) DO UPDATE SET
                clock_in = excluded.clock_in,
                clock_out = excluded.clock_out,
                late_entry = excluded.late_entry,
                overtime_hours = excluded.overtime_hours,
                status = excluded.status
        """, (emp_id, date_val, clock_in, clock_out, int(late), float(overtime), status))
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Log Attendance", f"Logged attendance for employee ID {emp_id} on {date_val} as {status}")
        return jsonify({"success": True, "message": "Attendance record logged successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --- FINANCE APIs ---

@app.route("/api/finance/records", methods=["GET"])
def get_finance_records():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM finance WHERE company_id = ? ORDER BY date DESC", (user["company_id"],))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(records)

@app.route("/api/finance/records", methods=["POST"])
def add_finance_record():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    f_type = data.get("type") 
    category = data.get("category")
    amount = data.get("amount")
    desc = data.get("description")
    date_val = data.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    
    if not f_type or not category or not amount:
        return jsonify({"error": "Type, Category, and Amount are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO finance (company_id, type, category, amount, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user["company_id"], f_type, category, float(amount), desc, date_val))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Add Finance Entry", f"Recorded {f_type} of ₹{amount} under {category}")
    return jsonify({"success": True, "message": "Finance entry recorded successfully"})

@app.route("/api/finance/records/<int:record_id>", methods=["DELETE"])
def delete_finance_record(record_id):
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT company_id FROM finance WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    if not row or row["company_id"] != user["company_id"]:
        conn.close()
        return jsonify({"error": "Record not found"}), 404
        
    cursor.execute("DELETE FROM finance WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Delete Finance Record", f"Deleted ledger record ID {record_id}.")
    return jsonify({"success": True, "message": "Transaction deleted successfully"})


@app.route("/api/finance/budgets", methods=["GET"])
def get_finance_budgets():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM department_budgets WHERE company_id = ?", (user["company_id"],))
    budgets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(budgets)

@app.route("/api/finance/budgets", methods=["POST"])
def save_finance_budget():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    dept = data.get("department")
    budget = data.get("budget")
    month = data.get("month", datetime.date.today().month)
    year = data.get("year", datetime.date.today().year)
    
    if not dept or budget is None:
        return jsonify({"error": "Department and Budget amount are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO department_budgets (company_id, department, budget, month, year)
        VALUES (?, ?, ?, ?, ?)
    """, (user["company_id"], dept, float(budget), int(month), int(year)))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Update Budget", f"Updated budget for {dept} to ₹{budget}")
    return jsonify({"success": True, "message": "Department budget updated successfully"})


# --- VENDORS / SUPPLIERS APIs ---

@app.route("/api/vendors", methods=["GET"])
def get_vendors():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE company_id = ?", (user["company_id"],))
    vendors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(vendors)

@app.route("/api/vendors", methods=["POST"])
def add_vendor():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    name = data.get("supplier_name")
    company = data.get("company")
    gst = data.get("gst_number")
    phone = data.get("phone")
    email = data.get("email")
    address = data.get("address")
    terms = data.get("payment_terms")
    balance = data.get("outstanding_balance", 0.0)
    
    if not name:
        return jsonify({"error": "Vendor name is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO suppliers (company_id, supplier_name, company, gst_number, phone, email, address, payment_terms, outstanding_balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user["company_id"], name, company, gst, phone, email, address, terms, float(balance)))
    conn.commit()
    conn.close()
    
    write_audit_log(user["company_id"], user["email"], "Add Vendor", f"Added procurement vendor {name}")
    return jsonify({"success": True, "message": "Vendor registered successfully"})


# --- INVENTORY & STOCK APIs ---

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, s.supplier_name, e.name as employee_name
        FROM inventory i
        LEFT JOIN suppliers s ON i.supplier_id = s.id
        LEFT JOIN employees e ON i.assigned_employee_id = e.id
        WHERE i.company_id = ?
    """, (user["company_id"],))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)

@app.route("/api/inventory", methods=["POST"])
def add_inventory():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    name = data.get("product_name")
    sku = data.get("sku_code")
    barcode = data.get("barcode")
    category = data.get("category")
    brand = data.get("brand")
    model = data.get("model")
    serial = data.get("serial_number")
    desc = data.get("description")
    price = data.get("purchase_price", 0.0)
    supplier_id = data.get("supplier_id")
    warehouse = data.get("warehouse", "Warehouse A")
    loc = data.get("location")
    stock = data.get("current_stock", 1)
    min_s = data.get("minimum_stock", 1)
    max_s = data.get("maximum_stock", 10)
    status = data.get("status", "Available")
    warranty = data.get("warranty_expiry")
    emp_id = data.get("assigned_employee_id")
    
    if not name or not category:
        return jsonify({"error": "Product name and category are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO inventory (
                company_id, product_name, sku_code, barcode, category, brand, model, serial_number, description,
                purchase_date, purchase_price, gst, supplier_id, warehouse, location, current_stock, minimum_stock, maximum_stock, status, warranty_expiry, assigned_employee_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'), ?, 18.0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["company_id"], name, sku, barcode, category, brand, model, serial, desc,
            float(price), supplier_id, warehouse, loc, int(stock), int(min_s), int(max_s), status, warranty, emp_id
        ))
        
        product_id = cursor.lastrowid
        
        # Log stock transaction
        cursor.execute("""
            INSERT INTO stock_transactions (company_id, product_id, type, quantity, date, time, user, reason)
            VALUES (?, ?, 'Stock In', ?, date('now'), time('now'), ?, 'Initial seed entry')
        """, (user["company_id"], product_id, int(stock), user["email"]))
        
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Add Stock Product", f"Added asset product {name} to {warehouse}")
        return jsonify({"success": True, "message": "Product added to inventory successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/inventory/assign", methods=["POST"])
def assign_inventory_asset():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    item_id = data.get("id")
    emp_id = data.get("assigned_employee_id") # null if returning
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    status = "Assigned" if emp_id else "Available"
    
    try:
        cursor.execute("""
            UPDATE inventory 
            SET assigned_employee_id = ?, status = ?
            WHERE id = ? AND company_id = ?
        """, (emp_id, status, item_id, user["company_id"]))
        
        # Log stock transaction
        tx_type = "Stock Out" if emp_id else "Return"
        reason = f"Assigned to employee ID {emp_id}" if emp_id else "Returned back to warehouse storage"
        
        cursor.execute("""
            INSERT INTO stock_transactions (company_id, product_id, type, quantity, date, time, user, reason)
            VALUES (?, ?, ?, 1, date('now'), time('now'), ?, ?)
        """, (user["company_id"], item_id, tx_type, user["email"], reason))
        
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Asset Assignment", f"Asset ID {item_id} status updated to {status}")
        return jsonify({"success": True, "message": "Asset status updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --- MARKET & INVESTMENTS APIs ---

@app.route("/api/investments/watchlist", methods=["GET"])
def get_watchlist():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Randomly fluctuate watchlist prices slightly to simulate live market data
    cursor.execute("SELECT * FROM market_watchlist WHERE company_id = ?", (user["company_id"],))
    rows = cursor.fetchall()
    
    watchlist = []
    for r in rows:
        pct = random.uniform(-1.5, 1.5)
        new_price = round(r["current_price"] * (1 + pct/100.0), 2)
        cursor.execute("""
            UPDATE market_watchlist 
            SET current_price = ?, change_percentage = ?
            WHERE id = ?
        """, (new_price, round(pct, 2), r["id"]))
        
        watchlist.append({
            "id": r["id"],
            "name": r["name"],
            "ticker": r["ticker"],
            "type": r["type"],
            "current_price": new_price,
            "change_percentage": round(pct, 2)
        })
        
    conn.commit()
    conn.close()
    return jsonify(watchlist)

@app.route("/api/investments/portfolio", methods=["GET"])
def get_portfolio():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM investment_portfolio WHERE company_id = ?", (user["company_id"],))
    rows = cursor.fetchall()
    
    portfolio = []
    for r in rows:
        # Cross-reference with watchlist if exists, else fluctuate
        cursor.execute("SELECT current_price, change_percentage FROM market_watchlist WHERE ticker = ? AND company_id = ?", (r["ticker"], user["company_id"]))
        match = cursor.fetchone()
        
        curr_p = r["current_price"]
        if match:
            curr_p = match["current_price"]
        else:
            curr_p = round(r["current_price"] * (1 + random.uniform(-0.5, 0.5)/100.0), 2)
            cursor.execute("UPDATE investment_portfolio SET current_price = ? WHERE id = ?", (curr_p, r["id"]))
            
        portfolio.append({
            "id": r["id"],
            "name": r["name"],
            "ticker": r["ticker"],
            "type": r["type"],
            "purchase_price": r["purchase_price"],
            "quantity": r["quantity"],
            "current_price": curr_p,
            "date_purchased": r["date_purchased"]
        })
        
    conn.commit()
    conn.close()
    return jsonify(portfolio)

@app.route("/api/investments/buy", methods=["POST"])
def buy_investment_asset():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    name = data.get("name")
    ticker = data.get("ticker")
    i_type = data.get("type", "Stock")
    price = data.get("purchase_price")
    qty = data.get("quantity")
    
    if not ticker or not price or not qty:
        return jsonify({"error": "Ticker, price, and quantity are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO investment_portfolio (company_id, name, ticker, type, purchase_price, quantity, current_price, date_purchased)
            VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
        """, (user["company_id"], name, ticker, i_type, float(price), float(qty), float(price)))
        
        conn.commit()
        write_audit_log(user["company_id"], user["email"], "Buy Investment", f"Purchased {qty} units of {ticker} at ₹{price}")
        return jsonify({"success": True, "message": f"Successfully purchased {qty} units of {ticker}!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# --- REPORTS APIs ---

@app.route("/api/reports/export", methods=["GET"])
def export_reports():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    role = user["role"]
    
    rep_type = request.args.get("type", "employees") 
    rep_format = request.args.get("format", "csv")
    preview = request.args.get("preview") == "true"
    
    # Enforce role-based security
    allowed = False
    if role in ["Admin", "Super Admin"]:
        allowed = True
    elif role == "HR Manager" and rep_type in ["employees", "attendance", "leaves", "recruitment", "audit"]:
        allowed = True
    elif role in ["Finance Manager", "Payroll Manager"] and rep_type in ["payroll", "tax", "finance", "audit"]:
        allowed = True
    elif role == "Inventory Manager" and rep_type in ["inventory", "vendor"]:
        allowed = True
    elif role == "Employee" and rep_type in ["payroll", "attendance"]:
        allowed = True
        
    if not allowed:
        return jsonify({"error": f"Access Denied: Your role '{role}' is not authorized to access '{rep_type}' reports."}), 403

    # Dynamic Filter Parsing
    department = request.args.get("department")
    employee_id = request.args.get("employee_id")
    status = request.args.get("status")
    category = request.args.get("category")
    warehouse = request.args.get("warehouse")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    month = request.args.get("month")
    year = request.args.get("year")
    
    # Employees cannot query other employee IDs
    if role == "Employee":
        employee_id = str(user["id"])

    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_params = []
    
    if rep_type == "employees":
        sql = "SELECT employee_id_code, name, email, department, designation, basic_salary, joining_date, status FROM employees WHERE company_id = ?"
        query_params.append(user["company_id"])
        if department:
            sql += " AND department = ?"
            query_params.append(department)
        if employee_id:
            sql += " AND id = ?"
            query_params.append(int(employee_id))
        if status:
            sql += " AND status = ?"
            query_params.append(status)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Emp Code", "Name", "Email", "Department", "Designation", "Basic Salary", "Joining Date", "Status"]
        
    elif rep_type == "payroll":
        sql = """
            SELECT e.employee_id_code, e.name, p.month, p.year, p.basic_salary, p.hra, p.da, p.bonus, p.gross_salary, p.pf, p.income_tax, p.net_salary
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            WHERE e.company_id = ?
        """
        query_params.append(user["company_id"])
        if department:
            sql += " AND e.department = ?"
            query_params.append(department)
        if employee_id:
            sql += " AND p.employee_id = ?"
            query_params.append(int(employee_id))
        if month:
            sql += " AND p.month = ?"
            query_params.append(int(month))
        if year:
            sql += " AND p.year = ?"
            query_params.append(int(year))
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Emp Code", "Name", "Month", "Year", "Basic Salary", "HRA", "DA", "Bonus", "Gross Salary", "PF", "Income Tax", "Net Salary"]
        
    elif rep_type == "finance":
        sql = "SELECT date, type, category, amount, description FROM finance WHERE company_id = ?"
        query_params.append(user["company_id"])
        if category:
            sql += " AND category = ?"
            query_params.append(category)
        if status: # Use as transaction Type (Income/Expense)
            sql += " AND type = ?"
            query_params.append(status)
        if start_date:
            sql += " AND date >= ?"
            query_params.append(start_date)
        if end_date:
            sql += " AND date <= ?"
            query_params.append(end_date)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Date", "Type", "Category", "Amount", "Description"]
        
    elif rep_type == "attendance":
        sql = """
            SELECT e.employee_id_code, e.name, a.date, a.clock_in, a.clock_out, a.late_entry, a.overtime_hours, a.status
            FROM attendance a
            JOIN employees e ON a.employee_id = e.id
            WHERE e.company_id = ?
        """
        query_params.append(user["company_id"])
        if department:
            sql += " AND e.department = ?"
            query_params.append(department)
        if employee_id:
            sql += " AND a.employee_id = ?"
            query_params.append(int(employee_id))
        if start_date:
            sql += " AND a.date >= ?"
            query_params.append(start_date)
        if end_date:
            sql += " AND a.date <= ?"
            query_params.append(end_date)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Emp Code", "Name", "Date", "Clock In", "Clock Out", "Late Minutes", "Overtime Hours", "Status"]
        
    elif rep_type == "leaves":
        sql = """
            SELECT e.employee_id_code, e.name, l.start_date, l.end_date, l.leave_type, l.reason, l.status
            FROM leave_requests l
            JOIN employees e ON l.employee_id = e.id
            WHERE e.company_id = ?
        """
        query_params.append(user["company_id"])
        if department:
            sql += " AND e.department = ?"
            query_params.append(department)
        if employee_id:
            sql += " AND l.employee_id = ?"
            query_params.append(int(employee_id))
        if status:
            sql += " AND l.status = ?"
            query_params.append(status)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Emp Code", "Name", "Start Date", "End Date", "Leave Type", "Reason", "Status"]
        
    elif rep_type == "recruitment":
        sql = "SELECT candidate_name, email, phone, designation, status, interview_date FROM recruitment WHERE company_id = ?"
        query_params.append(user["company_id"])
        if status:
            sql += " AND status = ?"
            query_params.append(status)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Candidate", "Email", "Phone", "Designation", "Status", "Interview Date"]
        
    elif rep_type == "inventory":
        sql = "SELECT product_name, sku_code, category, purchase_price, warehouse, status FROM inventory WHERE company_id = ?"
        query_params.append(user["company_id"])
        if category:
            sql += " AND category = ?"
            query_params.append(category)
        if warehouse:
            sql += " AND warehouse = ?"
            query_params.append(warehouse)
        if status:
            sql += " AND status = ?"
            query_params.append(status)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Asset Name", "SKU Code", "Category", "Purchase Cost", "Warehouse", "Status"]
        
    elif rep_type == "vendor":
        sql = "SELECT supplier_name, company, gst_number, phone, email, outstanding_balance FROM suppliers WHERE company_id = ?"
        query_params.append(user["company_id"])
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Supplier Name", "Company", "GST Number", "Phone", "Email", "Outstanding Balance"]
        
    elif rep_type == "tax":
        sql = """
            SELECT e.employee_id_code, e.name, p.year, sum(p.gross_salary) as total_gross, sum(p.pf) as total_pf, sum(p.income_tax) as total_tax
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            WHERE e.company_id = ?
        """
        query_params.append(user["company_id"])
        if department:
            sql += " AND e.department = ?"
            query_params.append(department)
        if employee_id:
            sql += " AND p.employee_id = ?"
            query_params.append(int(employee_id))
        sql += " GROUP BY p.employee_id, p.year"
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Emp Code", "Name", "Financial Year", "Total Gross Outlay", "Total PF Deducted", "Total Tax Deducted"]
        
    elif rep_type == "audit":
        sql = "SELECT user_email, action, details, timestamp FROM audit_logs WHERE company_id = ?"
        query_params.append(user["company_id"])
        if start_date:
            sql += " AND timestamp >= ?"
            query_params.append(start_date)
        if end_date:
            sql += " AND timestamp <= ?"
            query_params.append(end_date)
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["User Email", "Action Details", "Description", "Timestamp"]
        
    else: # Custom / AI Reports Fallback
        sql = "SELECT name, department, designation, basic_salary, status FROM employees WHERE company_id = ?"
        query_params.append(user["company_id"])
        cursor.execute(sql, tuple(query_params))
        rows = cursor.fetchall()
        headers = ["Name", "Department", "Designation", "Basic Salary", "Status"]
        
    # Get Company Name for Header Title Layouts
    cursor.execute("SELECT name FROM companies WHERE id = ?", (user["company_id"],))
    company_row = cursor.fetchone()
    company_name = company_row["name"] if company_row else "EnterpriseOS"
    conn.close()

    raw_data = [list(row) for row in rows]
    report_title = f"{rep_type.upper()} REPORT SUMMARY"

    # Audit log the generation event
    write_audit_log(user["company_id"], user["email"], "Generate Report", f"Generated {rep_type} report in {rep_format} format.")

    # 1. Preview mode (returns JSON overview)
    if preview:
        csv_data = ",".join(headers) + "\n"
        for r in raw_data:
            csv_data += ",".join([str(val).replace(",", ";") if val is not None else "" for val in r]) + "\n"
        return jsonify({
            "type": rep_type,
            "headers": headers,
            "data": raw_data,
            "csv_string": csv_data
        })

    # 2. Complete File Exports
    if rep_format == "csv":
        csv_out = generate_csv_report(headers, raw_data)
        mem_file = io.BytesIO(csv_out.encode('utf-8'))
        return send_file(
            mem_file,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"{rep_type}_report.csv"
        )
    elif rep_format == "excel":
        excel_out = generate_excel_report(headers, raw_data, title=report_title)
        mem_file = io.BytesIO(excel_out)
        return send_file(
            mem_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"{rep_type}_report.xlsx"
        )
    elif rep_format == "pdf":
        # Formulate some summary metrics for PDF layouts
        summary_metrics = {
            "Total Records / Count": len(raw_data)
        }
        if rep_type == "payroll" and len(raw_data) > 0:
            total_net = sum([row[11] for row in raw_data if isinstance(row[11], (int, float))])
            summary_metrics["Total Net Outlay"] = f"₹{total_net:,.2f}"
            summary_metrics["Net Outlay (in Words)"] = num_to_words(total_net)
        
        pdf_out = generate_pdf_report(
            headers, raw_data, 
            title=report_title, 
            company_name=company_name, 
            generated_by=user["name"],
            summary_metrics=summary_metrics
        )
        mem_file = io.BytesIO(pdf_out)
        return send_file(
            mem_file,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{rep_type}_report.pdf"
        )

    return jsonify({"error": "Invalid format"}), 400


# --- REPORT SCHEDULING & EMAIL SIMULATORS ---

@app.route("/api/reports/schedule", methods=["GET", "POST"])
def manage_scheduled_reports():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        data = request.get_json() or {}
        report_type = data.get("report_type", "employees")
        frequency = data.get("frequency", "Weekly")
        recipient_email = data.get("recipient_email", user["email"])
        rep_format = data.get("format", "pdf")
        
        cursor.execute("""
            INSERT INTO scheduled_reports (company_id, report_type, frequency, recipient_email, format)
            VALUES (?, ?, ?, ?, ?)
        """, (user["company_id"], report_type, frequency, recipient_email, rep_format))
        conn.commit()
        
        write_audit_log(user["company_id"], user["email"], "Schedule Report", f"Scheduled {report_type} report to send {frequency.lower()} to {recipient_email}")
        conn.close()
        return jsonify({"message": f"Successfully scheduled {report_type} report ({frequency})!"})
        
    # GET
    cursor.execute("SELECT id, report_type, frequency, recipient_email, format, created_at FROM scheduled_reports WHERE company_id = ?", (user["company_id"],))
    schedules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(schedules)


@app.route("/api/reports/email", methods=["POST"])
def email_report_now():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    rep_type = data.get("type", "employees")
    recipient_email = data.get("email", user["email"])
    rep_format = data.get("format", "pdf")
    
    # Simulate attachment data compilation
    attachment_dummy = b"Corporate Report Transcript Payload"
    filename = f"{rep_type}_report.{rep_format}"
    
    res = simulate_email_report(
        recipient_email,
        subject=f"EnterpriseOS Automated Summary - {rep_type.upper()}",
        report_title=f"{rep_type.upper()} Report",
        file_data=attachment_dummy,
        filename=filename
    )
    
    # Log delivery in audit
    write_audit_log(user["company_id"], user["email"], "Email Report", f"Emailed {rep_type} report in {rep_format} format to {recipient_email}.")
    
    # Save simulated log to Captive OTP simulated Sms/email banner
    return jsonify({
        "message": res["message"],
        "log_line": res["log_line"]
    })


@app.route("/api/reports/cloud_backup", methods=["POST"])
def cloud_backup_report():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    rep_type = data.get("type", "employees")
    rep_format = data.get("format", "pdf")
    
    # Log simulated backup event
    write_audit_log(user["company_id"], user["email"], "Cloud Backup", f"Backed up {rep_type} report in {rep_format} format to Enterprise Secure Storage Node.")
    
    return jsonify({
        "success": True,
        "message": f"Successfully uploaded '{rep_type}_report.{rep_format}' archive payload to cloud backups storage!"
    })



# --- SETTINGS APIs ---

@app.route("/api/settings/company", methods=["GET"])
def get_company_profile():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM companies WHERE id = ?", (user["company_id"],))
    comp = cursor.fetchone()
    conn.close()
    
    return jsonify({
        "company_name": comp["name"] if comp else "PayFlow Corp",
        "currency": "INR (₹)",
        "tax_regime": "New Regime",
        "email_notifications": True
    })

@app.route("/api/settings/company", methods=["POST"])
def update_company_profile():
    if "user" not in session or not is_admin_or_manager(session["user"]["role"]):
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    company_name = data.get("company_name")
    
    if company_name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE companies SET name = ? WHERE id = ?", (company_name, user["company_id"]))
        conn.commit()
        conn.close()
        
    write_audit_log(user["company_id"], user["email"], "Update Settings", "Updated company profile configuration")
    return jsonify({"success": True, "message": "Company configurations updated successfully!"})


# --- AI CHATBOT INTEGRATION API ---

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat_handler():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    message = data.get("message", "").strip().lower()
    
    response_text = "I am your HRMS AI Assistant. I can guide you on using the platform, explaining HRA, PF, taxes, and help you navigate modules."
    action = None
    
    # 1. Navigation intents
    if "dashboard" in message or "take me to home" in message:
        response_text = "Navigating you directly to the central Dashboard Analytics."
        action = {"redirect": "page-dashboard"}
    elif "employee" in message or "roster" in message or "staff" in message:
        response_text = "Opening the Employee Directory. You can manage employee profiles here."
        action = {"redirect": "page-employees"}
    elif "recruitment" in message or "candidate" in message or "hiring" in message:
        response_text = "Opening HR Management & Candidate pipelines."
        action = {"redirect": "page-hr-recruitment"}
    elif "payroll" in message or "salary" in message or "slips" in message:
        response_text = "Redirecting you to the Payroll Processing central panel."
        action = {"redirect": "page-payroll"}
    elif "finance" in message or "ledger" in message or "expense" in message:
        response_text = "Redirecting to the Company Finance Management ledger."
        action = {"redirect": "page-finance"}
    elif "attendance" in message or "clock" in message or "biometric" in message:
        response_text = "Redirecting you to Roster & Daily Attendance. You can simulate swiping card inputs here."
        action = {"redirect": "page-attendance"}
    elif "leave" in message or "apply leave" in message:
        response_text = "Opening Leave Management dashboard balances."
        action = {"redirect": "page-leaves"}
    elif "tax" in message or "slab" in message:
        response_text = "Opening progressive tax rules configuration."
        action = {"redirect": "page-taxslabs"}
    elif "report" in message or "export" in message:
        response_text = "Opening the Corporate Reports Export Center."
        action = {"redirect": "page-reports"}
    elif "analytics" in message or "chart" in message:
        response_text = "Navigating you to advanced analytical widgets."
        action = {"redirect": "page-analytics"}
    elif "settings" in message or "profile" in message:
        response_text = "Opening System Configuration & Settings."
        action = {"redirect": "page-settings"}
    elif "market" in message or "stock" in message or "investment" in message:
        response_text = "Opening the Market & Investments dashboard."
        action = {"redirect": "page-investments"}
        
    # 2. FAQ Policy intents
    elif "apply" in message and "leave" in message:
        response_text = "To apply for leave: Go to **Leave Management** in the sidebar, fill out the start date, end date, leave type, and click **Submit Application**."
    elif "download" in message and "slip" in message:
        response_text = "To download salary slips: Open **Payroll Module**, find your processed row in the table, click **Pay Slip**, and select **Print** or download PDF."
    elif "update" in message and "bank" in message:
        response_text = "To update bank accounts: Navigate to **Employee Management**, click **Edit** on the employee, scroll to the **Professional & KYC** section, modify Bank Account / IFSC Code, and save."
    elif "hra" in message:
        response_text = "**House Rent Allowance (HRA)** is a component provided for renting accommodation. In this system, HRA is calculated as **40% of the Basic Salary**."
    elif "pf" in message:
        response_text = "**Provident Fund (PF)** is calculated as **12% of the Basic Salary** and is deducted monthly for retirement savings."
    elif "gross" in message:
        response_text = "**Gross Salary** = Basic Salary + HRA (40%) + DA (10%) + Medical Allowance (₹1250) + Travel Allowance (₹1600) + performance bonuses."
    elif "net" in message:
        response_text = "**Net Salary** = Gross Salary - Deductions (PF + Income Tax / TDS + Professional Tax + Insurance)."
        
    # 3. Filter employees intent
    elif "show" in message and "department" in message:
        # e.g. "show IT department"
        match = re.search(r'department\s+(\w+)', message)
        dept = match.group(1).upper() if match else "IT"
        response_text = f"Filtering employee directory for the **{dept}** department."
        action = {"redirect": "page-employees", "search": dept}
        
    return jsonify({
        "response": response_text,
        "action": action
    })


# --- SIMULATION APIs ---

@app.route("/api/simulate/email_slip", methods=["POST"])
def simulate_email_slip():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    
    data = request.get_json() or {}
    recipient_email = data.get("email")
    subject = data.get("subject")
    body_html = data.get("body_html")
    
    if not recipient_email or not subject or not body_html:
        return jsonify({"error": "Recipient email, subject, and salary slip details are required"}), 400
        
    write_audit_log(user["company_id"], user["email"], "Email Pay Slip", f"Simulated sending salary slip to {recipient_email}")
    return jsonify({
        "success": True,
        "message": f"Salary slip email sent successfully to {recipient_email} (Simulated).",
        "details": {
            "to": recipient_email,
            "subject": subject,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    })

@app.route("/api/simulate/future", methods=["POST"])
def simulate_future():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = session["user"]
    data = request.get_json() or {}
    new_hires = int(data.get("new_hires", 0))
    avg_salary = float(data.get("avg_salary", 70000.0))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt, SUM(basic_salary) as sal FROM employees WHERE company_id = ? AND status = 'Active'", (user["company_id"],))
    stats = cursor.fetchone()
    conn.close()
    
    current_headcount = stats["cnt"] if stats["cnt"] else 0
    current_payroll = stats["sal"] if stats["sal"] else 0.0
    
    future_headcount = current_headcount + new_hires
    added_payroll = new_hires * avg_salary
    future_payroll = current_payroll + added_payroll
    
    # Calculate tax impacts (approximate at 15%)
    current_tax = current_payroll * 0.15
    future_tax = future_payroll * 0.15
    
    # Office space requirement (100 sq ft per employee)
    space_sqft = future_headcount * 100
    
    return jsonify({
        "current_headcount": current_headcount,
        "future_headcount": future_headcount,
        "current_payroll": current_payroll,
        "future_payroll": future_payroll,
        "added_payroll": added_payroll,
        "current_tax": current_tax,
        "future_tax": future_tax,
        "space_sqft": space_sqft
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
