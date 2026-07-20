// Client-side application state
let currentUser = null;
let currentCompanyId = null;
let charts = {};
let activeWindows = new Set();
let windowPositions = {};
let highestZIndex = 100;

// Email validation regex (matches backend)
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

// On DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
    setupWindowManager();
    setupTerminal();
    setupTimeMachine();
    setupClock();
});

// Toast Helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// System Clock
function setupClock() {
    setInterval(() => {
        const timeEl = document.getElementById('taskbar-clock');
        if (timeEl) {
            const now = new Date();
            timeEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }, 1000);
}

// Initialise App
async function initApp() {
    lucide.createIcons();
    
    // Check if user session exists
    try {
        const response = await fetch('/api/auth/session');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            currentCompanyId = data.user.company_id;
            document.getElementById('active-company-name').textContent = "Loading...";
            
            await loadCompaniesList();
            showWorkspace();
        } else {
            showLandingPage();
        }
    } catch (e) {
        showToast("Error checking session. Reconnecting...", "error");
        showLandingPage();
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Theme Toggle
    document.getElementById('btn-theme-toggle').addEventListener('click', toggleTheme);

    // Login Form
    document.getElementById('login-form').addEventListener('submit', handleLoginSubmit);
    
    // Signup Form
    document.getElementById('signup-form').addEventListener('submit', handleSignupSubmit);
    
    // Captcha Refresh Buttons
    document.getElementById('btn-refresh-captcha').addEventListener('click', () => {
        loadCaptcha('login');
    });
    document.getElementById('btn-refresh-signup-captcha').addEventListener('click', () => {
        loadCaptcha('signup');
    });
    
    // Company selection triggers demo credential loading
    document.getElementById('login-company').addEventListener('change', (e) => {
        loadDemoCredentials(e.target.value);
    });
    
    // Email real-time validation (login)
    document.getElementById('login-email').addEventListener('blur', (e) => {
        const hint = document.getElementById('email-validation-hint');
        if (e.target.value && !EMAIL_REGEX.test(e.target.value.trim())) {
            hint.classList.remove('hide');
        } else {
            hint.classList.add('hide');
        }
    });
    
    // Email real-time validation (signup)
    document.getElementById('signup-email').addEventListener('blur', (e) => {
        const hint = document.getElementById('signup-email-hint');
        if (e.target.value && !EMAIL_REGEX.test(e.target.value.trim())) {
            hint.classList.remove('hide');
        } else {
            hint.classList.add('hide');
        }
    });
    
    // Company Registration Template Selection
    document.querySelectorAll('.btn-template-select').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const template = e.currentTarget.getAttribute('data-template');
            document.getElementById('reg-company-name').value = template;
            showToast(`Selected ${template} workspace template!`, "info");
        });
    });

    // Register Company Form
    document.getElementById('register-company-form').addEventListener('submit', handleRegisterCompany);

    // Switch to register company
    document.getElementById('btn-show-register-company').addEventListener('click', (e) => {
        e.preventDefault();
        openRegisterCompanyModal();
    });

    // Logout
    document.getElementById('btn-logout').addEventListener('click', handleLogout);

    // Employee search and filter
    document.getElementById('employee-search').addEventListener('input', filterEmployees);
    document.getElementById('employee-filter-dept').addEventListener('change', filterEmployees);

    // Add Employee Button
    document.getElementById('btn-add-employee').addEventListener('click', () => {
        openEmployeeModal();
    });

    // Employee Submit Form
    document.getElementById('employee-form').addEventListener('submit', handleEmployeeSave);

    // Payroll Calculator overrides submit
    document.getElementById('payroll-calculation-form').addEventListener('submit', handleProcessSinglePayrollSubmit);

    // Bulk Payroll processing
    document.getElementById('btn-generate-bulk-payroll').addEventListener('click', runBulkPayroll);

    // Leave application submit
    const leaveForm = document.getElementById('leave-request-form');
    if (leaveForm) leaveForm.addEventListener('submit', handleLeaveRequestSubmit);

    // Slab settings events
    document.getElementById('btn-add-slab-row').addEventListener('click', addTaxSlabRow);
    document.getElementById('btn-save-slabs').addEventListener('click', saveTaxSlabs);

    // Phone verification click listeners
    document.getElementById('btn-trigger-phone-verify').addEventListener('click', () => {
        openPhoneVerificationModal();
    });
    document.getElementById('phone-verification-form').addEventListener('submit', handlePhoneVerificationSubmit);

    // Candidate Add Form
    const candForm = document.getElementById('candidate-form');
    if (candForm) candForm.addEventListener('submit', handleCandidateSave);
    const candStatusForm = document.getElementById('candidate-status-form');
    if (candStatusForm) candStatusForm.addEventListener('submit', handleCandidateStatusSave);

    // Finance Record Form
    const finForm = document.getElementById('finance-record-form');
    if (finForm) finForm.addEventListener('submit', handleFinanceRecordSave);

    // Settings Profile Form
    document.getElementById('settings-profile-form').addEventListener('submit', handleSettingsProfileSave);

    // Role Simulator dropdown
    document.getElementById('role-selector-sim').addEventListener('change', (e) => {
        currentUser.role = e.target.value;
        showToast(`Simulating session access level as ${e.target.value}`, "info");
        showWorkspace();
    });

    // Close Start Menu on Desktop click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.btn-start') && !e.target.closest('.start-menu')) {
            document.getElementById('start-menu').classList.add('hide');
        }
    });

    // Extended features AI/Inventory/Investments
    setupExtendedFeatures();
}

// Drag & Drop Window Manager Setup
function setupWindowManager() {
    const windows = document.querySelectorAll('.window');
    windows.forEach(win => {
        const header = win.querySelector('.window-header');
        
        // Window focusing
        win.addEventListener('mousedown', () => {
            focusWindow(win.id);
        });

        // Drag handlers
        let isDragging = false;
        let startX, startY, currentX, currentY;

        header.addEventListener('mousedown', (e) => {
            if (win.classList.contains('maximized')) return;
            isDragging = true;
            startX = e.clientX - win.offsetLeft;
            startY = e.clientY - win.offsetTop;
            focusWindow(win.id);
            document.addEventListener('mousemove', onDrag);
            document.addEventListener('mouseup', stopDrag);
        });

        function onDrag(e) {
            if (!isDragging) return;
            currentX = e.clientX - startX;
            currentY = e.clientY - startY;
            win.style.left = `${currentX}px`;
            win.style.top = `${currentY}px`;
            windowPositions[win.id] = { left: currentX, top: currentY };
        }

        function stopDrag() {
            isDragging = false;
            document.removeEventListener('mousemove', onDrag);
            document.removeEventListener('mouseup', stopDrag);
        }
    });
}

function focusWindow(winId) {
    const win = document.getElementById(winId);
    if (!win) return;
    highestZIndex += 1;
    win.style.zIndex = highestZIndex;

    // Set active tab on taskbar
    document.querySelectorAll('.taskbar-win-tab').forEach(tab => {
        if (tab.getAttribute('data-win') === winId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

function openWindow(winId) {
    // Management-only guards
    const isManagement = isManagementRole(currentUser.role);
    const win = document.getElementById(winId);
    if (!win) return;

    if (!isManagement && ['win-employees', 'win-hr-recruitment', 'win-payroll', 'win-finance', 'win-inventory', 'win-taxslabs', 'win-reports', 'win-analytics'].includes(winId)) {
        showToast("Access Denied: Management authorization required.", "error");
        return;
    }

    win.classList.remove('hide');
    activeWindows.add(winId);
    focusWindow(winId);
    
    // Set default position if first time
    if (!windowPositions[winId]) {
        const offset = (activeWindows.size * 25) % 150;
        win.style.left = `${180 + offset}px`;
        win.style.top = `${60 + offset}px`;
        windowPositions[winId] = { left: 180 + offset, top: 60 + offset };
    }

    // Call page hooks
    triggerWindowPageHooks(winId);

    // Update Taskbar
    updateTaskbarWindows();
    document.getElementById('start-menu').classList.add('hide');
}

function triggerWindowPageHooks(winId) {
    switch (winId) {
        case 'win-employees': loadEmployees(); break;
        case 'win-hr-recruitment': loadRecruitment(); break;
        case 'win-payroll': initPayrollMonthYear(); loadPayrollProcessor(); break;
        case 'win-finance': loadFinanceModule(); break;
        case 'win-inventory': loadInventory(); break;
        case 'win-investments': loadInvestments(); break;
        case 'win-taxslabs': loadTaxSlabs(); break;
        case 'win-analytics': loadAnalyticsCharts(); break;
        case 'win-leaves': loadAttendanceLogs(); loadLeaveRequests(); populateApprovingManagers(); break;
        case 'win-settings': loadSettingsPage(); break;
        case 'win-reports': loadReportFiltersList(); loadScheduledReports(); break;
    }
}

function minimizeWindow(winId) {
    const win = document.getElementById(winId);
    if (win) win.classList.add('hide');
    activeWindows.delete(winId);
    updateTaskbarWindows();
}

function toggleMaximizeWindow(winId) {
    const win = document.getElementById(winId);
    if (win) win.classList.toggle('maximized');
}

function closeWindow(winId) {
    const win = document.getElementById(winId);
    if (win) {
        win.classList.add('hide');
        win.classList.remove('maximized');
    }
    activeWindows.delete(winId);
    updateTaskbarWindows();
}

function toggleStartMenu() {
    const menu = document.getElementById('start-menu');
    menu.classList.toggle('hide');
}

function updateTaskbarWindows() {
    const list = document.getElementById('taskbar-windows-list');
    list.innerHTML = '';

    const appTitles = {
        'win-employees': '👥 HR Roster',
        'win-hr-recruitment': '💼 Recruitment',
        'win-payroll': '💰 Payroll',
        'win-finance': '📊 Finance',
        'win-inventory': '📦 Inventory',
        'win-investments': '📈 Investments',
        'win-taxslabs': '🧮 Tax Slabs',
        'win-reports': '📄 Reports',
        'win-analytics': '📉 Analytics',
        'win-terminal': '📟 Terminal',
        'win-digitaltwin': '🗺️ Digital Twin',
        'win-timemachine': '🕰️ Time Machine',
        'win-leaves': '📅 Attendance & Leaves',
        'win-settings': '⚙️ Settings'
    };

    activeWindows.forEach(winId => {
        const tab = document.createElement('div');
        tab.className = 'taskbar-win-tab';
        tab.setAttribute('data-win', winId);
        tab.textContent = appTitles[winId] || winId;
        tab.addEventListener('click', () => {
            const win = document.getElementById(winId);
            if (win.classList.contains('hide')) {
                win.classList.remove('hide');
                focusWindow(winId);
            } else {
                minimizeWindow(winId);
            }
        });
        list.appendChild(tab);
    });
}

// Landing Page scrolling
function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

function showLandingPage() {
    document.body.classList.remove('OS-body');
    document.getElementById('landing-container').classList.remove('hide');
    document.getElementById('login-container').classList.add('hide');
    document.getElementById('workspace-container').classList.add('hide');
    document.getElementById('os-taskbar').classList.add('hide');
}

function showAuthFromLanding(tab = 'signin') {
    document.body.classList.remove('OS-body');
    document.getElementById('landing-container').classList.add('hide');
    document.getElementById('login-container').classList.remove('hide');
    switchAuthTab(tab);
    loadCompaniesList();
}

function switchAuthTab(tab = 'signin') {
    const tabSignin = document.getElementById('tab-signin');
    const tabSignup = document.getElementById('tab-signup');
    const formSignin = document.getElementById('login-form');
    const formSignup = document.getElementById('signup-form');
    
    if (tab === 'signin') {
        tabSignin.classList.add('active');
        tabSignup.classList.remove('active');
        formSignin.classList.remove('hide');
        formSignup.classList.add('hide');
        loadCaptcha('login');
    } else {
        tabSignin.classList.remove('active');
        tabSignup.classList.add('active');
        formSignin.classList.add('hide');
        formSignup.classList.remove('hide');
        loadCaptcha('signup');
    }
}

// Theme Toggle Handler
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        themeIcon.setAttribute('data-lucide', 'moon');
        showToast("Switched to Light Mode", "info");
    } else {
        body.classList.add('dark-mode');
        themeIcon.setAttribute('data-lucide', 'sun');
        showToast("Switched to Dark OS Desktop Mode", "info");
    }
    lucide.createIcons();
}

// Fetch and load captcha
async function loadCaptcha(target = 'login') {
    try {
        const response = await fetch('/api/auth/captcha');
        const data = await response.json();
        
        if (target === 'signup') {
            document.getElementById('signup-captcha-display').textContent = data.question;
            document.getElementById('signup-captcha').value = '';
        } else {
            document.getElementById('captcha-display').textContent = data.question;
            document.getElementById('login-captcha').value = '';
        }
    } catch (e) {
        if (target === 'signup') {
            document.getElementById('signup-captcha-display').textContent = "Error";
        } else {
            document.getElementById('captcha-display').textContent = "Error";
        }
    }
}

// Fetch and load companies list
async function loadCompaniesList() {
    try {
        const response = await fetch('/api/auth/companies');
        const companies = await response.json();
        
        const loginSelect = document.getElementById('login-company');
        loginSelect.innerHTML = '<option value="" disabled selected>Select Company</option>';
        
        companies.forEach(company => {
            const opt = document.createElement('option');
            opt.value = company.id;
            opt.textContent = company.name;
            loginSelect.appendChild(opt);
        });
        
        if (currentCompanyId) {
            loginSelect.value = currentCompanyId;
            const activeCompany = companies.find(c => c.id === currentCompanyId);
            if (activeCompany) {
                document.getElementById('active-company-name').textContent = activeCompany.name;
            }
        }
        populateSignupCompanySelect(companies);
    } catch (e) {
        showToast("Error loading companies list", "error");
    }
}

function populateSignupCompanySelect(companies) {
    const signupSelect = document.getElementById('signup-company');
    if (!signupSelect) return;
    signupSelect.innerHTML = '<option value="" disabled selected>Select Company to Join</option>';
    
    companies.forEach(company => {
        const opt = document.createElement('option');
        opt.value = company.id;
        opt.textContent = company.name;
        signupSelect.appendChild(opt);
    });
}

// Load Demo Credentials
async function loadDemoCredentials(companyId) {
    const box = document.getElementById('demo-credentials-box');
    const list = document.getElementById('demo-credentials-list');
    
    try {
        const response = await fetch(`/api/auth/credentials?company_id=${companyId}`);
        const creds = await response.json();
        
        if (creds.length === 0) {
            box.classList.add('hide');
            return;
        }
        
        list.innerHTML = '';
        creds.forEach(cred => {
            const item = document.createElement('div');
            item.className = 'demo-cred-item';
            item.innerHTML = `
                <span class="cred-role badge ${cred.role === 'Admin' ? 'badge-active' : 'badge-role'}">${cred.role}</span>
                <span class="cred-detail">${cred.email} / <code>${cred.password}</code></span>
            `;
            item.addEventListener('click', () => {
                document.getElementById('login-email').value = cred.email;
                document.getElementById('login-password').value = cred.password;
                showToast(`Auto-filled credentials for ${cred.name}`, "info");
            });
            list.appendChild(item);
        });
        
        box.classList.remove('hide');
    } catch (e) {
        box.classList.add('hide');
    }
}

// Handle Login Form Submit
async function handleLoginSubmit(e) {
    e.preventDefault();
    const company_id = document.getElementById('login-company').value;
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const captcha = document.getElementById('login-captcha').value;
    
    if (!EMAIL_REGEX.test(email)) {
        showToast("Invalid email format.", "error");
        document.getElementById('email-validation-hint').classList.remove('hide');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_id, email, password, captcha })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            currentCompanyId = data.company_id;
            
            showToast("Successfully Authenticated!", "success");
            await loadCompaniesList();
            showWorkspace();
        } else {
            showToast(data.error || "Authentication failed", "error");
            loadCaptcha('login');
        }
    } catch (err) {
        showToast("Server connection error", "error");
    }
}

// Handle Signup Form Submit
async function handleSignupSubmit(e) {
    e.preventDefault();
    const company_id = document.getElementById('signup-company').value;
    const name = document.getElementById('signup-name').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const phone = document.getElementById('signup-phone').value.trim();
    const password = document.getElementById('signup-password').value;
    const captcha = document.getElementById('signup-captcha').value;
    
    if (!EMAIL_REGEX.test(email)) {
        showToast("Invalid email format.", "error");
        document.getElementById('signup-email-hint').classList.remove('hide');
        return;
    }
    
    if (password.length < 6) {
        showToast("Password must be at least 6 characters", "error");
        return;
    }
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_id, name, email, phone, password, captcha })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            currentCompanyId = data.company_id;
            showToast(data.message || "Account created successfully!", "success");
            await loadCompaniesList();
            showWorkspace();
        } else {
            showToast(data.error || "Signup failed", "error");
            loadCaptcha('signup');
        }
    } catch (err) {
        showToast("Server connection error", "error");
    }
}

// Handle Logout with Custom Modern Overlay Animation
async function handleLogout() {
    const logoutOverlay = document.getElementById('logout-overlay');
    logoutOverlay.classList.remove('hide');
    document.getElementById('start-menu').classList.add('hide');
    
    setTimeout(async () => {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            currentUser = null;
            currentCompanyId = null;
            activeWindows.clear();
            showToast("Signed out successfully", "info");
            logoutOverlay.classList.add('hide');
            showLandingPage();
        } catch (e) {
            showToast("Sign out failed", "error");
            logoutOverlay.classList.add('hide');
        }
    }, 1500);
}

// Handle Register Company Modal Submit
async function handleRegisterCompany(e) {
    e.preventDefault();
    const name = document.getElementById('reg-company-name').value;
    
    try {
        const response = await fetch('/api/auth/companies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`Workspace initialized for ${name}!`, "success");
            closeRegisterCompanyModal();
            await loadCompaniesList();
            document.getElementById('login-company').value = data.id;
            loadDemoCredentials(data.id);
        } else {
            showToast(data.error || "Failed to create company", "error");
        }
    } catch (err) {
        showToast("Server error", "error");
    }
}

// Show Main Workspace
function showWorkspace() {
    document.body.classList.add('OS-body');
    document.getElementById('login-container').classList.add('hide');
    document.getElementById('workspace-container').classList.remove('hide');
    document.getElementById('os-taskbar').classList.remove('hide');
    
    // Set Profile Badge
    document.getElementById('user-display-name').textContent = currentUser.name;
    document.getElementById('user-display-role').textContent = currentUser.role;
    document.getElementById('user-avatar-char').textContent = currentUser.name.charAt(0).toUpperCase();

    // Set phone status verification badge
    updatePhoneVerificationUI();

    // Adjust UI options based on role
    const isManagement = isManagementRole(currentUser.role);
    if (isManagement) {
        document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hide'));
        document.getElementById('role-selector-sim').value = currentUser.role;
    } else {
        document.querySelectorAll('.admin-only').forEach(el => el.classList.add('hide'));
    }

    // Default open Terminal and Twin maps to show off the system!
    openWindow('win-terminal');
}

function isManagementRole(role) {
    return ['Admin', 'Super Admin', 'HR Manager', 'Finance Manager', 'Payroll Manager'].includes(role);
}

// Update Phone Verification State in Sidebar
function updatePhoneVerificationUI() {
    const badge = document.getElementById('user-phone-status-badge');
    const link = document.getElementById('btn-trigger-phone-verify');
    
    const isVerified = currentUser && currentUser.phone_verified;
    
    if (isVerified) {
        badge.className = "phone-status-badge verified";
        badge.textContent = "✓";
        badge.title = "Phone Number Verified";
        if (link) link.style.display = "none";
    } else {
        badge.className = "phone-status-badge unverified";
        badge.textContent = "⚠️";
        badge.title = "Phone Number Unverified";
        if (link) link.style.display = "block";
    }
}

// CAPTCHA Refresh Actions
function openRegisterCompanyModal() {
    document.getElementById('modal-register-company').classList.remove('hide');
}
function closeRegisterCompanyModal() {
    document.getElementById('modal-register-company').classList.add('hide');
}
function closeOtpBanner() {
    document.getElementById('otp-banner').classList.add('hide');
}


// ==================== EMPLOYEES DIRECTORY ==================== //
let employeesList = [];

async function loadEmployees() {
    try {
        const response = await fetch('/api/employees');
        employeesList = await response.json();
        
        // Dynamically extract departments for filter dropdown
        const deptFilter = document.getElementById('employee-filter-dept');
        const currentSelected = deptFilter.value;
        deptFilter.innerHTML = '<option value="">All Departments</option>';
        const depts = [...new Set(employeesList.map(e => e.department))];
        depts.forEach(dept => {
            const opt = document.createElement('option');
            opt.value = dept;
            opt.textContent = dept;
            deptFilter.appendChild(opt);
        });
        deptFilter.value = currentSelected;

        renderEmployeesTable(employeesList);
    } catch (e) {
        showToast("Error loading employee roster", "error");
    }
}

function renderEmployeesTable(list) {
    const tbody = document.getElementById('employees-table-body');
    tbody.innerHTML = '';
    
    list.forEach(emp => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><code>${emp.employee_id_code}</code></td>
            <td><strong>${emp.name}</strong></td>
            <td>${emp.email}</td>
            <td>${emp.department}</td>
            <td>${emp.designation}</td>
            <td>₹${emp.basic_salary.toLocaleString('en-IN')}</td>
            <td><span class="badge ${emp.role === 'Admin' ? 'badge-active' : 'badge-role'}">${emp.role}</span></td>
            <td><span class="badge ${emp.status === 'Active' ? 'badge-active' : 'badge-inactive'}">${emp.status}</span></td>
            <td class="text-right">
                <button class="btn btn-secondary btn-sm" onclick="editEmployee(${emp.id})">Edit</button>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteEmployee(${emp.id}, '${emp.name}')">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterEmployees() {
    const query = document.getElementById('employee-search').value.toLowerCase().trim();
    const dept = document.getElementById('employee-filter-dept').value;
    
    let filtered = employeesList;
    if (query) {
        filtered = filtered.filter(e => 
            e.name.toLowerCase().includes(query) || 
            e.employee_id_code.toLowerCase().includes(query) ||
            e.department.toLowerCase().includes(query) ||
            e.designation.toLowerCase().includes(query)
        );
    }
    if (dept) {
        filtered = filtered.filter(e => e.department === dept);
    }
    renderEmployeesTable(filtered);
}

// Add/Edit Modals
function openEmployeeModal(emp = null) {
    const title = document.getElementById('employee-modal-title');
    const form = document.getElementById('employee-form');
    form.reset();

    if (emp) {
        title.textContent = "Edit Employee Profile";
        document.getElementById('emp-edit-id').value = emp.id;
        document.getElementById('emp-code').value = emp.employee_id_code;
        document.getElementById('emp-code').setAttribute('readonly', 'true');
        document.getElementById('emp-name').value = emp.name;
        document.getElementById('emp-email').value = emp.email;
        document.getElementById('emp-gender').value = emp.gender;
        document.getElementById('emp-father').value = emp.father_name || '';
        document.getElementById('emp-mother').value = emp.mother_name || '';
        document.getElementById('emp-dob').value = emp.dob || '';
        document.getElementById('emp-age').value = emp.age || 25;
        document.getElementById('emp-blood').value = emp.blood_group || '';
        
        document.getElementById('emp-phone').value = emp.phone || '';
        document.getElementById('emp-emergency').value = emp.emergency_contact || '';
        document.getElementById('emp-address').value = emp.address || '';
        document.getElementById('emp-city').value = emp.city || '';
        document.getElementById('emp-state').value = emp.state || '';
        document.getElementById('emp-pincode').value = emp.pin_code || '';
        
        document.getElementById('emp-dept').value = emp.department;
        document.getElementById('emp-designation').value = emp.designation;
        document.getElementById('emp-joining').value = emp.joining_date;
        document.getElementById('emp-pan').value = emp.pan_number || '';
        document.getElementById('emp-aadhaar').value = emp.aadhaar_number || '';
        document.getElementById('emp-exp').value = emp.experience || 0;
        document.getElementById('emp-education').value = emp.education || '';
        document.getElementById('emp-photo').value = emp.photo || '';
        document.getElementById('emp-basic').value = emp.basic_salary;
        document.getElementById('emp-bank').value = emp.bank_account || '';
        document.getElementById('emp-ifsc').value = emp.ifsc_code || '';
        document.getElementById('emp-role').value = emp.role;
        document.getElementById('emp-status').value = emp.status;
        document.getElementById('emp-password').value = '';
    } else {
        title.textContent = "Add Employee Record";
        document.getElementById('emp-edit-id').value = '';
        document.getElementById('emp-code').removeAttribute('readonly');
        document.getElementById('emp-password').value = 'employee123';
    }

    document.getElementById('modal-employee').classList.remove('hide');
}

function closeEmployeeModal() {
    document.getElementById('modal-employee').classList.add('hide');
}

async function editEmployee(id) {
    try {
        const response = await fetch('/api/employees');
        const emps = await response.json();
        const emp = emps.find(e => e.id === id);
        if (emp) {
            openEmployeeModal(emp);
        }
    } catch (e) {
        showToast("Error fetching employee details", "error");
    }
}

async function handleEmployeeSave(e) {
    e.preventDefault();
    const id = document.getElementById('emp-edit-id').value;
    const employee_id_code = document.getElementById('emp-code').value.trim();
    const name = document.getElementById('emp-name').value.trim();
    const email = document.getElementById('emp-email').value.trim();
    const gender = document.getElementById('emp-gender').value;
    const father_name = document.getElementById('emp-father').value.trim();
    const mother_name = document.getElementById('emp-mother').value.trim();
    const dob = document.getElementById('emp-dob').value;
    const age = parseInt(document.getElementById('emp-age').value);
    const blood_group = document.getElementById('emp-blood').value.trim();
    
    const phone = document.getElementById('emp-phone').value.trim();
    const emergency_contact = document.getElementById('emp-emergency').value.trim();
    const address = document.getElementById('emp-address').value.trim();
    const city = document.getElementById('emp-city').value.trim();
    const state = document.getElementById('emp-state').value.trim();
    const pin_code = document.getElementById('emp-pincode').value.trim();
    
    const department = document.getElementById('emp-dept').value.trim();
    const designation = document.getElementById('emp-designation').value.trim();
    const joining_date = document.getElementById('emp-joining').value;
    const pan_number = document.getElementById('emp-pan').value.trim();
    const aadhaar_number = document.getElementById('emp-aadhaar').value.trim();
    const experience = parseFloat(document.getElementById('emp-exp').value);
    const education = document.getElementById('emp-education').value.trim();
    const photo = document.getElementById('emp-photo').value.trim();
    const basic_salary = parseFloat(document.getElementById('emp-basic').value);
    const bank_account = document.getElementById('emp-bank').value.trim();
    const ifsc_code = document.getElementById('emp-ifsc').value.trim();
    const role = document.getElementById('emp-role').value;
    const status = document.getElementById('emp-status').value;
    const password = document.getElementById('emp-password').value;

    const payload = {
        employee_id_code, name, email, gender, father_name, mother_name, dob, age, blood_group,
        phone, emergency_contact, address, city, state, pin_code, department, designation, joining_date,
        pan_number, aadhaar_number, experience, education, photo, basic_salary, bank_account, ifsc_code, role, status
    };
    if (password) payload.password = password;

    try {
        let response;
        if (id) {
            response = await fetch(`/api/employees/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            response = await fetch('/api/employees', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }
        
        const data = await response.json();
        if (response.ok) {
            showToast(data.message || "Employee details saved successfully!", "success");
            closeEmployeeModal();
            loadEmployees();
        } else {
            showToast(data.error || "Failed to save employee details", "error");
        }
    } catch (err) {
        showToast("Error connecting to server", "error");
    }
}

async function confirmDeleteEmployee(id, name) {
    if (confirm(`Are you sure you want to delete employee "${name}"?`)) {
        try {
            const response = await fetch(`/api/employees/${id}`, { method: 'DELETE' });
            if (response.ok) {
                showToast("Employee deleted from registry", "success");
                loadEmployees();
            } else {
                const data = await response.json();
                showToast(data.error || "Failed to delete employee", "error");
            }
        } catch (e) {
            showToast("Server connection error", "error");
        }
    }
}


// ==================== RECRUITMENT MODULE ==================== //
async function loadRecruitment() {
    try {
        const response = await fetch('/api/hr/recruitment');
        const list = await response.json();
        
        const tbody = document.getElementById('recruitment-table-body');
        tbody.innerHTML = '';
        
        list.forEach(c => {
            const tr = document.createElement('tr');
            const dateStr = c.interview_date || 'TBD';
            const offerStr = c.offer_letter_sent ? 'Sent (PDF Available)' : 'TBD';

            tr.innerHTML = `
                <td><strong>${c.candidate_name}</strong></td>
                <td>${c.email}</td>
                <td>${c.phone || 'N/A'}</td>
                <td>${c.designation}</td>
                <td>${dateStr}</td>
                <td><span class="badge badge-active">${c.status}</span></td>
                <td>${offerStr}</td>
                <td class="text-right">
                    <button class="btn btn-secondary btn-sm" onclick="openUpdateStatusModal(${c.id}, '${c.status}', '${c.feedback || ''}', '${c.interview_date || ''}', ${c.offer_letter_sent})">Update</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast("Error loading candidate trackers", "error");
    }
}

function openAddCandidateModal() {
    document.getElementById('candidate-form').reset();
    document.getElementById('modal-candidate').classList.remove('hide');
}
function closeCandidateModal() {
    document.getElementById('modal-candidate').classList.add('hide');
}

async function handleCandidateSave(e) {
    e.preventDefault();
    const candidate_name = document.getElementById('cand-name').value.trim();
    const email = document.getElementById('cand-email').value.trim();
    const phone = document.getElementById('cand-phone').value.trim();
    const designation = document.getElementById('cand-desig').value.trim();

    try {
        const response = await fetch('/api/hr/recruitment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_name, email, phone, designation })
        });
        if (response.ok) {
            showToast("Candidate successfully added to pipeline!", "success");
            closeCandidateModal();
            loadRecruitment();
        }
    } catch (e) {
        showToast("Network request failed", "error");
    }
}

function openUpdateStatusModal(id, status, feedback, interviewDate, offerSent) {
    document.getElementById('cand-status-id').value = id;
    document.getElementById('cand-status-select').value = status;
    document.getElementById('cand-feedback').value = feedback;
    document.getElementById('cand-interview-date').value = interviewDate;
    document.getElementById('cand-offer-sent').checked = offerSent === 1;
    document.getElementById('modal-candidate-status').classList.remove('hide');
}
function closeCandidateStatusModal() {
    document.getElementById('modal-candidate-status').classList.add('hide');
}

async function handleCandidateStatusSave(e) {
    e.preventDefault();
    const id = document.getElementById('cand-status-id').value;
    const status = document.getElementById('cand-status-select').value;
    const feedback = document.getElementById('cand-feedback').value.trim();
    const interview_date = document.getElementById('cand-interview-date').value;
    const offer_letter_sent = document.getElementById('cand-offer-sent').checked ? 1 : 0;

    try {
        const response = await fetch(`/api/hr/recruitment/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status, feedback, interview_date, offer_letter_sent })
        });
        if (response.ok) {
            showToast("Candidate details successfully updated", "success");
            closeCandidateStatusModal();
            loadRecruitment();
        }
    } catch (e) {
        showToast("Error updating candidate details", "error");
    }
}


// ==================== PAYROLL PROCESSOR ==================== //
function initPayrollMonthYear() {
    const monthSelect = document.getElementById('payroll-month');
    const yearSelect = document.getElementById('payroll-year');
    
    // Set to current date if not set
    const now = new Date();
    if (!monthSelect.value) monthSelect.value = now.getMonth() + 1;
    if (!yearSelect.value) yearSelect.value = now.getFullYear();
}

async function loadPayrollProcessor() {
    const month = document.getElementById('payroll-month').value;
    const year = document.getElementById('payroll-year').value;
    
    try {
        const response = await fetch(`/api/payroll?month=${month}&year=${year}`);
        const list = await response.json();
        
        const tbody = document.getElementById('payroll-table-body');
        tbody.innerHTML = '';
        
        list.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${r.employee_id_code}</code></td>
                <td><strong>${r.employee_name}</strong></td>
                <td>${r.department}</td>
                <td>₹${r.basic_salary.toLocaleString('en-IN')}</td>
                <td>${r.unpaid_leaves}</td>
                <td>₹${r.gross_salary.toLocaleString('en-IN')}</td>
                <td>₹${r.pf.toLocaleString('en-IN')}</td>
                <td>₹${r.income_tax.toLocaleString('en-IN')}</td>
                <td><strong>₹${r.net_salary.toLocaleString('en-IN')}</strong></td>
                <td><span class="badge badge-active">Processed</span></td>
                <td class="text-right">
                    <button class="btn btn-secondary btn-sm" onclick="openSinglePayrollModal(${r.employee_id}, '${r.employee_name}', ${r.basic_salary}, ${r.unpaid_leaves})">Recalculate</button>
                    <button class="btn btn-primary btn-sm" onclick="previewPayslip(${r.id})">Pay Slip</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast("Error loading payroll calculations", "error");
    }
}

async function runBulkPayroll() {
    const month = document.getElementById('payroll-month').value;
    const year = document.getElementById('payroll-year').value;
    const workingDays = document.getElementById('payroll-working-days').value;
    
    try {
        const response = await fetch('/api/payroll/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ month, year, working_days: workingDays })
        });
        const data = await response.json();
        if (response.ok) {
            showToast(`Generated payroll for ${data.processed_count} employees!`, "success");
            loadPayrollProcessor();
        } else {
            showToast(data.error, "error");
        }
    } catch (e) {
        showToast("Failed to run payroll generator", "error");
    }
}

function openSinglePayrollModal(empId, empName, basic, unpaidLeavesAuto) {
    document.getElementById('payroll-calc-emp-id').value = empId;
    document.getElementById('payroll-calc-emp-name').value = empName;
    document.getElementById('payroll-calc-basic').value = `₹${basic.toLocaleString('en-IN')}`;
    document.getElementById('payroll-calc-bonus').value = 0;
    
    const hint = document.getElementById('unpaid-leaves-auto-text');
    hint.textContent = `Auto: ${unpaidLeavesAuto} leaves detected`;
    document.getElementById('payroll-calc-unpaid-leaves').value = unpaidLeavesAuto;
    
    document.getElementById('modal-process-payroll').classList.remove('hide');
}
function closeProcessPayrollModal() {
    document.getElementById('modal-process-payroll').classList.add('hide');
}

async function handleProcessSinglePayrollSubmit(e) {
    e.preventDefault();
    const empId = document.getElementById('payroll-calc-emp-id').value;
    const month = document.getElementById('payroll-month').value;
    const year = document.getElementById('payroll-year').value;
    const workingDays = document.getElementById('payroll-working-days').value;
    const bonus = document.getElementById('payroll-calc-bonus').value;
    const unpaid_leaves = document.getElementById('payroll-calc-unpaid-leaves').value;

    try {
        const response = await fetch('/api/payroll/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                month, year, working_days: workingDays,
                employee_ids: [parseInt(empId)],
                bonus, unpaid_leaves
            })
        });
        if (response.ok) {
            showToast("Payroll processed successfully!", "success");
            closeProcessPayrollModal();
            loadPayrollProcessor();
        }
    } catch (e) {
        showToast("Failed to process single payroll", "error");
    }
}


// ==================== PAYSLIP PREVIEW & PDF ==================== //
let activePayslipRecord = null;

async function previewPayslip(recordId) {
    try {
        const response = await fetch('/api/payroll');
        const list = await response.json();
        const record = list.find(r => r.id === recordId);
        
        if (record) {
            activePayslipRecord = record;
            
            document.getElementById('slip-company-name').textContent = document.getElementById('active-company-name').textContent.toUpperCase();
            
            const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
            document.getElementById('slip-period').textContent = `${months[record.month - 1]} ${record.year}`;
            
            document.getElementById('slip-emp-code').textContent = record.employee_id_code;
            document.getElementById('slip-emp-name').textContent = record.employee_name;
            document.getElementById('slip-emp-dept').textContent = record.department;
            document.getElementById('slip-emp-desig').textContent = record.designation;
            document.getElementById('slip-working-days').textContent = record.working_days;
            document.getElementById('slip-leaves').textContent = record.unpaid_leaves;
            
            document.getElementById('slip-basic').textContent = record.basic_salary.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-hra').textContent = record.hra.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-da').textContent = record.da.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-medical').textContent = record.medical_allowance.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-travel').textContent = record.travel_allowance.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-bonus').textContent = record.bonus.toLocaleString('en-IN', {minimumFractionDigits:2});
            
            const totalGross = record.basic_salary + record.hra + record.da + record.medical_allowance + record.travel_allowance + record.bonus;
            document.getElementById('slip-gross').textContent = totalGross.toLocaleString('en-IN', {minimumFractionDigits:2});
            
            document.getElementById('slip-pf').textContent = record.pf.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-pt').textContent = record.professional_tax.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-tax').textContent = record.income_tax.toLocaleString('en-IN', {minimumFractionDigits:2});
            document.getElementById('slip-insurance').textContent = record.insurance.toLocaleString('en-IN', {minimumFractionDigits:2});
            
            const totalDeductions = record.pf + record.professional_tax + record.income_tax + record.insurance;
            document.getElementById('slip-deductions').textContent = totalDeductions.toLocaleString('en-IN', {minimumFractionDigits:2});
            
            document.getElementById('slip-net-payable').textContent = `₹${record.net_salary.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
            
            const roundNet = Math.round(record.net_salary);
            document.getElementById('slip-net-words').textContent = `Rupees ${numToWords(roundNet)} Only`;

            document.getElementById('modal-payslip').classList.remove('hide');
        }
    } catch (e) {
        showToast("Error rendering salary details", "error");
    }
}

function closePaySlipModal() {
    document.getElementById('modal-payslip').classList.add('hide');
}

function printPaySlip() {
    window.print();
}

async function sendSimulatedEmailSlip() {
    if (!activePayslipRecord) return;
    
    const bodyHtml = `
        <h3>Your Salary Slip for month ${activePayslipRecord.month}/${activePayslipRecord.year} has been generated.</h3>
        <p>Net payable take-home salary is: <strong>₹${activePayslipRecord.net_salary.toLocaleString('en-IN')}</strong></p>
    `;
    
    try {
        const response = await fetch('/api/simulate/email_slip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: activePayslipRecord.email || "recipient@gmail.com",
                subject: `Salary Pay Slip - Month ${activePayslipRecord.month}/${activePayslipRecord.year}`,
                body_html: bodyHtml
            })
        });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            
            // Dispatch simulation event to system capture logs
            document.getElementById('simulated-otp-code').textContent = "EMAIL_DISPATCHED";
            document.getElementById('otp-banner').classList.remove('hide');
        }
    } catch (e) {
        showToast("Simulated SMTP dispatch failed", "error");
    }
}


// ==================== ATTENDANCE MODULE ==================== //
async function loadAttendanceLogs() {
    try {
        const response = await fetch('/api/attendance');
        const list = await response.json();
        
        const tbody = document.getElementById('attendance-table-body');
        tbody.innerHTML = '';
        
        list.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${r.employee_name}</strong><br><small class="text-muted">${r.employee_id_code}</small></td>
                <td>${r.date}</td>
                <td>${r.clock_in || '—'}</td>
                <td>${r.clock_out || '—'}</td>
                <td>${r.late_entry} min</td>
                <td>${r.overtime_hours} hrs</td>
                <td><span class="badge ${r.status === 'Present' ? 'badge-active' : 'badge-inactive'}">${r.status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast("Error fetching attendance rosters", "error");
    }
}

async function simulateClockIn() {
    try {
        const response = await fetch('/api/attendance/clock_in', { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            loadAttendanceLogs();
        }
    } catch (e) {
        showToast("Simulation swipe error", "error");
    }
}

async function simulateClockOut() {
    try {
        const response = await fetch('/api/attendance/clock_out', { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            loadAttendanceLogs();
        }
    } catch (e) {
        showToast("Simulation swipe error", "error");
    }
}


// ==================== LEAVE MODULE ==================== //
async function loadLeaveRequests() {
    try {
        const response = await fetch('/api/leave_requests');
        const list = await response.json();
        
        const tbody = document.getElementById('leaves-table-body');
        tbody.innerHTML = '';
        
        const isManagement = isManagementRole(currentUser.role);
        
        list.forEach(r => {
            const tr = document.createElement('tr');
            
            let statusBadge = 'badge-role';
            if (r.status === 'Approved') statusBadge = 'badge-active';
            else if (r.status === 'Rejected') statusBadge = 'badge-inactive';

            let actionBtn = '';
            if (isManagement && r.status === 'Pending') {
                actionBtn = `
                    <button class="btn btn-success btn-sm" onclick="approveLeave(${r.id}, 'Approved')">Approve</button>
                    <button class="btn btn-danger btn-sm" onclick="approveLeave(${r.id}, 'Rejected')">Reject</button>
                `;
            }

            // Parse approver from reason
            let approverName = 'Any Manager';
            let displayReason = r.reason || '';
            if (r.reason && r.reason.startsWith('[Approver: ')) {
                const match = r.reason.match(/^\[Approver: ([^\]]+)\]\s*(.*)$/);
                if (match) {
                    approverName = match[1];
                    displayReason = match[2];
                }
            }

            tr.innerHTML = `
                <td><strong>${r.employee_name || currentUser.name}</strong></td>
                <td>${r.start_date} to ${r.end_date}</td>
                <td>${r.leave_type}</td>
                <td>${displayReason}</td>
                <td><span class="badge badge-role">${approverName}</span></td>
                <td><span class="badge ${statusBadge}">${r.status}</span></td>
                <td class="admin-only text-right">${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });
        
        const pendingCount = list.filter(l => l.status === 'Pending').length;
        const badge = document.getElementById('pending-leaves-badge');
        if (badge) {
            if (pendingCount > 0) {
                badge.textContent = pendingCount;
                badge.classList.remove('hide');
            } else {
                badge.classList.add('hide');
            }
        }
    } catch (e) {
        showToast("Error loading leave balances", "error");
    }
}

async function handleLeaveRequestSubmit(e) {
    e.preventDefault();
    const start_date = document.getElementById('leave-start-date').value;
    const end_date = document.getElementById('leave-end-date').value;
    const leave_type = document.getElementById('leave-type').value;
    const approver = document.getElementById('leave-approver-select').value;
    const reasonText = document.getElementById('leave-reason').value.trim();
    const reason = `[Approver: ${approver}] ${reasonText}`;

    try {
        const response = await fetch('/api/leave_requests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_date, end_date, leave_type, reason })
        });
        if (response.ok) {
            showToast("Leave application successfully submitted", "success");
            document.getElementById('leave-request-form').reset();
            loadLeaveRequests();
        }
    } catch (e) {
        showToast("Submission failed", "error");
    }
}

async function approveLeave(id, status) {
    try {
        const response = await fetch(`/api/leave_requests/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (response.ok) {
            showToast(`Leave application marked as ${status}!`, "success");
            loadLeaveRequests();
        }
    } catch (e) {
        showToast("Failed to process approval", "error");
    }
}


// ==================== FINANCE MODULE ==================== //
async function loadFinanceModule() {
    try {
        const response = await fetch('/api/finance/records');
        const list = await response.json();
        
        const tbody = document.getElementById('finance-table-body');
        tbody.innerHTML = '';
        
        list.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${r.date}</td>
                <td><span class="badge ${r.type === 'Income' ? 'badge-active' : 'badge-inactive'}">${r.type}</span></td>
                <td>${r.category}</td>
                <td><strong>₹${r.amount.toLocaleString('en-IN')}</strong></td>
                <td>${r.description || ''}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="deleteFinanceRecord(${r.id})" style="padding: 2px 6px; font-size: 0.75rem;">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast("Error loading financial ledger", "error");
    }
}

async function deleteFinanceRecord(id) {
    if (!confirm("Are you sure you want to delete this transaction record?")) return;
    try {
        const response = await fetch(`/api/finance/records/${id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showToast("Transaction deleted", "success");
            loadFinanceModule();
        } else {
            showToast("Failed to delete transaction", "error");
        }
    } catch (e) {
        showToast("Error deleting transaction", "error");
    }
}

async function handleFinanceRecordSave(e) {
    e.preventDefault();
    const type = document.getElementById('fin-type').value;
    const category = document.getElementById('fin-category').value.trim();
    const amount = document.getElementById('fin-amount').value;
    const date = document.getElementById('fin-date').value;
    const description = document.getElementById('fin-desc').value.trim();

    try {
        const response = await fetch('/api/finance/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, category, amount, date, description })
        });
        if (response.ok) {
            showToast("Financial transaction logged", "success");
            document.getElementById('finance-record-form').reset();
            loadFinanceModule();
        }
    } catch (e) {
        showToast("Connection error saving transaction", "error");
    }
}


// ==================== TAX SLABS MODULE ==================== //
async function loadTaxSlabs() {
    try {
        const response = await fetch('/api/tax_slabs');
        const slabs = await response.json();
        
        const container = document.getElementById('tax-slabs-container');
        container.innerHTML = '';
        
        slabs.forEach(slab => {
            addSlabRowElement(slab.min_income, slab.max_income, slab.tax_rate * 100);
        });
    } catch (e) {
        showToast("Error loading tax configurations", "error");
    }
}

function addSlabRowElement(min = 0, max = '', rate = 0) {
    const container = document.getElementById('tax-slabs-container');
    const div = document.createElement('div');
    div.className = 'slab-row';
    div.innerHTML = `
        <div class="form-group-inline">
            <label>Min (₹)</label>
            <input type="number" class="slab-min" value="${min}" required>
        </div>
        <div class="form-group-inline">
            <label>Max (₹)</label>
            <input type="number" class="slab-max" value="${max === null ? '' : max}" placeholder="Open ended">
        </div>
        <div class="form-group-inline">
            <label>Rate (%)</label>
            <input type="number" class="slab-rate" value="${rate}" min="0" max="100" required>
        </div>
        <button type="button" class="btn btn-danger btn-sm" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(div);
}

function addTaxSlabRow() {
    addSlabRowElement();
}

async function saveTaxSlabs() {
    const rows = document.querySelectorAll('.slab-row');
    const slabs = [];
    
    for (let r of rows) {
        const min = parseFloat(r.querySelector('.slab-min').value);
        const maxVal = r.querySelector('.slab-max').value;
        const max = maxVal === '' ? null : parseFloat(maxVal);
        const rate = parseFloat(r.querySelector('.slab-rate').value) / 100.0;
        
        if (isNaN(min) || isNaN(rate)) {
            showToast("Missing min income or tax rate parameters", "error");
            return;
        }
        slabs.push({ min_income: min, max_income: max, tax_rate: rate });
    }
    
    try {
        const response = await fetch('/api/tax_slabs', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(slabs)
        });
        if (response.ok) {
            showToast("Progressive tax rules saved and activated!", "success");
            loadTaxSlabs();
        }
    } catch (e) {
        showToast("Error updating slabs settings", "error");
    }
}


// ==================== ANALYTICS GRAPHICS ==================== //
async function loadAnalyticsCharts() {
    try {
        const response = await fetch('/api/payroll');
        const payroll = await response.json();
        
        const empResp = await fetch('/api/employees');
        const emps = await empResp.json();

        // 1. Payroll Monthly outlay line chart
        const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const outlays = Array(12).fill(0);
        payroll.forEach(p => {
            if (p.year === 2026) outlays[p.month - 1] += p.gross_salary;
        });

        renderLineChart('chart-payroll-trend', months, outlays, 'Gross Outlay (₹)');

        // 2. Department headcount pie chart
        const deptCounts = {};
        emps.forEach(e => {
            deptCounts[e.department] = (deptCounts[e.department] || 0) + 1;
        });
        
        renderPieChart('chart-dept-distribution', Object.keys(deptCounts), Object.values(deptCounts));

        // 3. Salary brackets bar chart
        const brackets = ["0-50K", "50K-100K", "100K-150K", "150K+"];
        const salaryBuckets = Array(4).fill(0);
        emps.forEach(e => {
            const basic = e.basic_salary;
            if (basic <= 50000) salaryBuckets[0]++;
            else if (basic <= 100000) salaryBuckets[1]++;
            else if (basic <= 150000) salaryBuckets[2]++;
            else salaryBuckets[3]++;
        });

        renderBarChart('chart-salary-histogram', brackets, salaryBuckets, 'Employees');

        // 4. Department average salary bar chart
        const deptSalaries = {};
        const deptNames = Object.keys(deptCounts);
        deptNames.forEach(d => {
            const deptEmps = emps.filter(e => e.department === d);
            const sum = deptEmps.reduce((acc, curr) => acc + curr.basic_salary, 0);
            deptSalaries[d] = sum / deptEmps.length;
        });

        renderBarChart('chart-dept-salary', Object.keys(deptSalaries), Object.values(deptSalaries), 'Average Basic (₹)');

    } catch (e) {
        showToast("Error updating analytical grids", "error");
    }
}

function renderLineChart(canvasId, labels, data, labelTitle) {
    if (charts[canvasId]) charts[canvasId].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: labelTitle,
                data: data,
                borderColor: '#6366f1',
                tension: 0.3,
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function renderPieChart(canvasId, labels, data) {
    if (charts[canvasId]) charts[canvasId].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function renderBarChart(canvasId, labels, data, datasetLabel) {
    if (charts[canvasId]) charts[canvasId].destroy();
    const ctx = document.getElementById(canvasId).getContext('2d');
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: data,
                backgroundColor: '#6366f1'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}


// ==================== SYSTEM SETTINGS MODULE ==================== //
async function loadSettingsPage() {
    try {
        const response = await fetch('/api/settings/company');
        const data = await response.json();
        
        document.getElementById('set-company-name').value = data.company_name;
        document.getElementById('set-currency').value = data.currency.startsWith("INR") ? "INR" : "USD";
        document.getElementById('set-regime').value = data.tax_regime;
    } catch (e) {}
}

async function handleSettingsProfileSave(e) {
    e.preventDefault();
    const company_name = document.getElementById('set-company-name').value;
    
    try {
        const response = await fetch('/api/settings/company', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ company_name })
        });
        if (response.ok) {
            showToast("Company configurations saved!", "success");
            document.getElementById('active-company-name').textContent = company_name;
        }
    } catch (err) {
        showToast("Error updating company configurations", "error");
    }
}

async function triggerDbBackup() {
    window.location.href = '/api/backup';
}
async function triggerDbRestore() {
    try {
        const response = await fetch('/api/backup/restore', { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
        }
    } catch (e) {
        showToast("Database restoration failed", "error");
    }
}


// ==================== OS COMMAND TERMINAL CLI ==================== //
function setupTerminal() {
    const form = document.getElementById('terminal-input-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const input = document.getElementById('terminal-input-field');
        const val = input.value.trim();
        input.value = '';

        if (!val) return;
        executeTerminalCommand(val);
    });
}

function executeTerminalCommand(cmdString) {
    const output = document.getElementById('terminal-output');
    
    // Print echo command
    const echoLine = document.createElement('div');
    echoLine.innerHTML = `<span class="prompt-symbol">admin@enterprise-os:~$</span> ${cmdString}`;
    output.appendChild(echoLine);

    const parts = cmdString.split(' ');
    const cmd = parts[0].toLowerCase();
    const arg = parts.slice(1).join(' ');

    let result = '';

    switch (cmd) {
        case 'help':
            result = `
                Available Commands:<br>
                - <strong class="color-purple">help</strong>: List available commands.<br>
                - <strong class="color-purple">clear</strong>: Clear terminal screen.<br>
                - <strong class="color-purple">redirect &lt;app&gt;</strong>: Open OS application (e.g. redirect payroll).<br>
                - <strong class="color-purple">kpis</strong>: Print active enterprise statistics.<br>
                - <strong class="color-purple">search &lt;name&gt;</strong>: Filter employees and focus directory.<br>
                - <strong class="color-purple">tax-slabs</strong>: View current progressive slabs.
            `;
            break;
        case 'clear':
            output.innerHTML = '';
            return;
        case 'redirect':
            const appName = arg.toLowerCase();
            const winMapping = {
                'employees': 'win-employees', 'roster': 'win-employees', 'hr': 'win-hr-recruitment',
                'recruitment': 'win-hr-recruitment', 'payroll': 'win-payroll', 'finance': 'win-finance',
                'inventory': 'win-inventory', 'investments': 'win-investments', 'tax': 'win-taxslabs',
                'reports': 'win-reports', 'analytics': 'win-analytics', 'terminal': 'win-terminal',
                'digitaltwin': 'win-digitaltwin', 'timemachine': 'win-timemachine', 'settings': 'win-settings'
            };
            const targetWin = winMapping[appName];
            if (targetWin) {
                openWindow(targetWin);
                result = `Application [${appName}] loaded and focused successfully.`;
            } else {
                result = `Error: Application [${arg}] not recognized. Type redirect &lt;app&gt;`;
            }
            break;
        case 'kpis':
            result = `
                Company KPI Summary (Live Data):<br>
                - Active Headcount: 6 Employees<br>
                - Gross Monthly Payroll: ₹583,000<br>
                - Security Status: 100% Secure (CAPTCHA Activated)<br>
                - Database: SQLite persistent storage
            `;
            break;
        case 'search':
            if (!arg) {
                result = `Error: Please provide a search term. Example: search priya`;
            } else {
                openWindow('win-employees');
                document.getElementById('employee-search').value = arg;
                filterEmployees();
                result = `Searching employee database for terms matching "${arg}"...`;
            }
            break;
        case 'tax-slabs':
            result = `
                New Tax Regime Slab Brackets:<br>
                - 0 to 3L: Exempt (0%)<br>
                - 3L to 7L: 5% tax slab<br>
                - 7L to 10L: 10% tax slab<br>
                - 10L to 15L: 15% tax slab<br>
                - 15L+: 20% tax slab
            `;
            break;
        default:
            result = `Command not recognized: "${cmd}". Type "help" for guidelines.`;
    }

    const resLine = document.createElement('div');
    resLine.innerHTML = result;
    output.appendChild(resLine);
    output.scrollTop = output.scrollHeight;
}


// ==================== COMPANY DIGITAL TWIN SENSORS ==================== //
function showZoneDetails(zoneName) {
    const diag = document.getElementById('twin-diag-output');
    
    let diagText = '';
    
    switch (zoneName) {
        case 'IT':
            diagText = `
                <strong>Zone: IT Department & Server Room</strong><br>
                - Location: Floor 2, Building A<br>
                - Active Headcount: 43 Devs Online<br>
                - Current Temperature: 21°C (AC Optimal)<br>
                - Server Health: 99.8% (SSL certificates valid)<br>
                - Active Projects: Project Alpha, Beta On-time
            `;
            break;
        case 'HR':
            diagText = `
                <strong>Zone: Human Resources Suite</strong><br>
                - Location: Floor 1, Building A<br>
                - Headcount: 2 Recruiters active<br>
                - Interview pipeline: 3 Candidates (Offer Letters pending)<br>
                - Onboarding Status: 100% compliant documents
            `;
            break;
        case 'Finance':
            diagText = `
                <strong>Zone: Finance Management Hub</strong><br>
                - Location: Floor 1, Building A<br>
                - Ledger Balance: Healthy (Transactions logged)<br>
                - Monthly Outlay: ₹583,000 (Jul 2026)<br>
                - Taxes Collected: ₹104,940
            `;
            break;
        case 'Warehouse':
            diagText = `
                <strong>Zone: Warehouse Logistics Center</strong><br>
                - Location: Ground Floor, Annex<br>
                - Stock count: 5 ThinkPads, 10 Monitors, 15 Chairs<br>
                - Inventory Value: ₹160,500<br>
                - <span class="color-red">Alert:</span> ThinkPads below threshold (Min: 2, Current: 2)<br>
                - Restocking Recommendation: Order 10 keyboards
            `;
            break;
    }
    
    diag.innerHTML = diagText;
}


// ==================== AI TIME MACHINE TIMELINE ==================== //
function setupTimeMachine() {
    const slider = document.getElementById('timemachine-slider');
    if (!slider) return;

    slider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value);
        
        let headcount = 6;
        let outlay = 583000;
        let tax = 104940;

        if (val === 2025) {
            headcount = 4;
            outlay = 380000;
            tax = 57000;
        } else if (val === 2027) {
            headcount = 12;
            outlay = 1100000;
            tax = 220000;
        }

        document.getElementById('sim-headcount').textContent = `${headcount} Employees`;
        document.getElementById('sim-outlay').textContent = `₹${outlay.toLocaleString('en-IN')}`;
        document.getElementById('sim-annual-tax').textContent = `₹${tax.toLocaleString('en-IN')}`;
    });
}

async function simulateHiringCost() {
    const new_hires = document.getElementById('sim-new-hires').value;
    const avg_salary = document.getElementById('sim-avg-salary').value;
    
    try {
        const response = await fetch('/api/simulate/future', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_hires, avg_salary })
        });
        const data = await response.json();
        
        const out = document.getElementById('sim-forecast-output');
        out.innerHTML = `
            <strong>AI Forecast Diagnostic Results:</strong><br>
            - Projected Headcount: ${data.future_headcount} (Current: ${data.current_headcount})<br>
            - Payroll Outlay Increase: +₹${data.added_payroll.toLocaleString()} /month<br>
            - Projected Monthly Payroll: ₹${data.future_payroll.toLocaleString()} /month<br>
            - Office Space Required: ${data.space_sqft} sq ft (100 sq ft/employee allocated)
        `;
        out.classList.remove('hide');
    } catch (e) {
        showToast("Error projecting future hiring budgets", "error");
    }
}


// ==================== EXTENDED PORTAL FEATURES ==================== //

function setupExtendedFeatures() {
    // AI Chat Input Form
    const aiForm = document.getElementById('ai-chat-input-form');
    if (aiForm) aiForm.addEventListener('submit', handleAiChatSubmit);

    // Inventory Product Form
    const invForm = document.getElementById('inventory-asset-form');
    if (invForm) invForm.addEventListener('submit', handleInventorySave);

    // Assign Asset Form
    const assignForm = document.getElementById('assign-asset-form');
    if (assignForm) assignForm.addEventListener('submit', handleAssignAsset);

    // Periodic Market Watchlist updates (simulating live ticking)
    setInterval(() => {
        if (activeWindows.has('win-investments')) {
            loadWatchlist();
        }
    }, 4000);
}

// AI Chatbot Window Actions
function toggleAiChatWindow() {
    const win = document.getElementById('ai-chat-window');
    win.classList.toggle('hide');
}

function sendAiQuickMessage(msg) {
    document.getElementById('ai-chat-input-text').value = msg;
    const form = document.getElementById('ai-chat-input-form');
    const event = new Event('submit', { cancelable: true });
    form.dispatchEvent(event);
}

async function handleAiChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('ai-chat-input-text');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    appendAiMessage(msg, 'ai-sent');

    try {
        const response = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });
        const data = await response.json();
        
        appendAiMessage(data.response, 'ai-received');

        // Handle navigation or search actions
        if (data.action) {
            if (data.action.redirect) {
                // Map page tabs to OS Window openings
                const redirectMappings = {
                    'page-dashboard': 'win-terminal',
                    'page-employees': 'win-employees',
                    'page-hr-recruitment': 'win-hr-recruitment',
                    'page-payroll': 'win-payroll',
                    'page-finance': 'win-finance',
                    'page-attendance': 'win-employees',
                    'page-leaves': 'win-employees',
                    'page-taxslabs': 'win-taxslabs',
                    'page-reports': 'win-reports',
                    'page-analytics': 'win-analytics',
                    'page-settings': 'win-settings',
                    'page-investments': 'win-investments'
                };
                const targetWin = redirectMappings[data.action.redirect];
                if (targetWin) openWindow(targetWin);
            }
            if (data.action.search && data.action.redirect === 'page-employees') {
                openWindow('win-employees');
                document.getElementById('employee-search').value = data.action.search;
                filterEmployees();
            }
        }
    } catch (err) {
        appendAiMessage("Sorry, I am having trouble connecting to my knowledge base right now.", 'ai-received');
    }
}

function appendAiMessage(text, className) {
    const container = document.getElementById('ai-chat-messages');
    const div = document.createElement('div');
    div.className = `ai-msg ${className}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// Inventory & Assets Management
async function loadInventory() {
    try {
        const response = await fetch('/api/inventory');
        const items = await response.json();

        // Calculate Stats
        document.getElementById('kpi-inventory-count').textContent = items.length;
        const totalVal = items.reduce((acc, curr) => acc + (curr.purchase_price || 0), 0);
        document.getElementById('kpi-inventory-value').textContent = `₹${totalVal.toLocaleString('en-IN', {maximumFractionDigits: 0})}`;
        const assignedVal = items.filter(i => i.status === 'Assigned').length;
        document.getElementById('kpi-inventory-assigned').textContent = assignedVal;

        // Render Table
        const tbody = document.getElementById('inventory-table-body');
        tbody.innerHTML = '';
        
        items.forEach(item => {
            const tr = document.createElement('tr');
            const priceStr = item.purchase_price ? `₹${item.purchase_price.toLocaleString('en-IN')}` : '₹0';
            const assigneeName = item.employee_name || 'Unassigned';
            
            let badgeClass = 'badge-role';
            if (item.status === 'Available') badgeClass = 'badge-active';
            else if (item.status === 'Assigned') badgeClass = 'badge-role';
            else if (item.status === 'Under Maintenance') badgeClass = 'badge-inactive';

            const actionBtn = item.status === 'Available' 
                ? `<button class="btn btn-secondary btn-sm" onclick="openAssignAssetModal(${item.id})">Assign</button>`
                : `<button class="btn btn-danger btn-sm" onclick="returnAsset(${item.id})">Return</button>`;

            tr.innerHTML = `
                <td><strong>${item.product_name}</strong><br><small class="text-muted">${item.brand} | ${item.model || ''}</small></td>
                <td><code>${item.sku_code || ''}</code></td>
                <td>${item.category}</td>
                <td>${priceStr}</td>
                <td>${item.warehouse}</td>
                <td>${assigneeName}</td>
                <td><span class="badge ${badgeClass}">${item.status}</span></td>
                <td class="text-right">${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });

        loadEmployeesDropdownForAssets();
    } catch (e) {
        showToast("Error loading company inventory assets", "error");
    }
}

async function handleInventorySave(e) {
    e.preventDefault();
    const product_name = document.getElementById('inv-name').value.trim();
    const category = document.getElementById('inv-category').value;
    const sku_code = document.getElementById('inv-sku').value.trim();
    const purchase_price = parseFloat(document.getElementById('inv-price').value);
    const warehouse = document.getElementById('inv-warehouse').value;

    try {
        const response = await fetch('/api/inventory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name, category, sku_code, purchase_price, warehouse })
        });
        
        if (response.ok) {
            showToast("Asset successfully registered into inventory stock!", "success");
            document.getElementById('inventory-asset-form').reset();
            loadInventory();
        } else {
            const data = await response.json();
            showToast(data.error || "Failed to add asset", "error");
        }
    } catch (err) {
        showToast("Server connection error", "error");
    }
}

async function loadEmployeesDropdownForAssets() {
    try {
        const response = await fetch('/api/employees');
        const emps = await response.json();
        const select = document.getElementById('assign-asset-employee-select');
        select.innerHTML = '<option value="" disabled selected>Select Employee</option>';
        emps.forEach(emp => {
            const opt = document.createElement('option');
            opt.value = emp.id;
            opt.textContent = `${emp.name} (${emp.employee_id_code})`;
            select.appendChild(opt);
        });
    } catch (e) {}
}

function openAssignAssetModal(itemId) {
    document.getElementById('assign-asset-product-id').value = itemId;
    document.getElementById('modal-assign-asset').classList.remove('hide');
}

function closeAssignAssetModal() {
    document.getElementById('modal-assign-asset').classList.add('hide');
}

async function handleAssignAsset(e) {
    e.preventDefault();
    const id = document.getElementById('assign-asset-product-id').value;
    const assigned_employee_id = document.getElementById('assign-asset-employee-select').value;

    try {
        const response = await fetch('/api/inventory/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, assigned_employee_id })
        });
        if (response.ok) {
            showToast("Asset successfully assigned to employee", "success");
            closeAssignAssetModal();
            loadInventory();
        } else {
            const data = await response.json();
            showToast(data.error || "Assignment failed", "error");
        }
    } catch (err) {
        showToast("Server error", "error");
    }
}

async function returnAsset(itemId) {
    try {
        const response = await fetch('/api/inventory/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: itemId, assigned_employee_id: null })
        });
        if (response.ok) {
            showToast("Asset returned back to warehouse storage", "success");
            loadInventory();
        }
    } catch (e) {
        showToast("Server connection error", "error");
    }
}

// Market & Investments Portfolio
async function loadInvestments() {
    await loadWatchlist();
    try {
        const response = await fetch('/api/investments/portfolio');
        const portfolio = await response.json();
        
        const tbody = document.getElementById('investments-portfolio-body');
        tbody.innerHTML = '';
        
        portfolio.forEach(item => {
            const tr = document.createElement('tr');
            const totalVal = item.current_price * item.quantity;
            const returnPct = ((item.current_price - item.purchase_price) / item.purchase_price * 100).toFixed(2);
            const returnClass = returnPct >= 0 ? 'price-up' : 'price-down';

            tr.innerHTML = `
                <td><strong>${item.name}</strong><br><small class="text-muted">${item.ticker}</small></td>
                <td><span class="badge badge-role">${item.type}</span></td>
                <td>₹${item.purchase_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                <td>${item.quantity}</td>
                <td>₹${item.current_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                <td><strong>₹${totalVal.toLocaleString('en-IN', {maximumFractionDigits: 0})}</strong><br><small class="${returnClass}">${returnPct >= 0 ? '+' : ''}${returnPct}%</small></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        showToast("Failed to load investment portfolio data", "error");
    }
}

async function loadWatchlist() {
    try {
        const response = await fetch('/api/investments/watchlist');
        const watchlist = await response.json();
        
        const tbody = document.getElementById('investments-watchlist-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        watchlist.forEach(item => {
            const tr = document.createElement('tr');
            const changeClass = item.change_percentage >= 0 ? 'price-up' : 'price-down';
            const changeSign = item.change_percentage >= 0 ? '+' : '';

            tr.innerHTML = `
                <td><strong>${item.ticker}</strong></td>
                <td>${item.name}</td>
                <td>₹${item.current_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                <td class="${changeClass}">${changeSign}${item.change_percentage}%</td>
                <td><button class="btn btn-primary btn-sm" onclick="buyWatchlistAsset('${item.ticker}', '${item.name}', ${item.current_price}, '${item.type}')">Buy Asset</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {}
}

async function buyWatchlistAsset(ticker, name, price, type) {
    const qty = prompt(`Current market rate for ${ticker} is ₹${price.toLocaleString()}. Enter amount/quantity to purchase:`, "10");
    if (!qty || isNaN(qty) || parseFloat(qty) <= 0) return;

    try {
        const response = await fetch('/api/investments/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker, name, purchase_price: price, quantity: parseFloat(qty), type })
        });
        if (response.ok) {
            showToast(`Asset order placed! Purchased ${qty} units of ${ticker}`, "success");
            loadInvestments();
        } else {
            const data = await response.json();
            showToast(data.error || "Order execution failed", "error");
        }
    } catch (err) {
        showToast("Server network error", "error");
    }
}

// Reports Download Center
async function triggerReportExport() {
    const type = document.getElementById('report-domain').value;
    const format = document.getElementById('report-format').value;

    try {
        const response = await fetch(`/api/reports/export?type=${type}&format=${format}`);
        const data = await response.json();

        if (format === 'csv') {
            const blob = new Blob([data.csv_string], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", `${type}_report_${new Date().toISOString().slice(0, 10)}.csv`);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showToast("CSV report generated and downloaded successfully!", "success");
        } else if (format === 'excel') {
            showToast("Excel spreadsheet layout compiled and downloaded! (Simulated)", "success");
        } else {
            showToast("PDF document compilation completed. View in Print preview.", "success");
            const repWindow = window.open("", "_blank");
            repWindow.document.write(`
                <html>
                <head>
                    <title>${type.toUpperCase()} REPORT</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 40px; color: #333; }
                        h1 { color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
                        th { background: #f1f5f9; }
                    </style>
                </head>
                <body>
                    <h1>${type.toUpperCase()} REPORT</h1>
                    <p>Generated on: ${new Date().toLocaleString()}</p>
                    <table>
                        <thead>
                            <tr>${data.headers.map(h => `<th>${h}</th>`).join('')}</tr>
                        </thead>
                        <tbody>
                            ${data.data.map(row => `<tr>${row.map(cell => `<td>${cell || ''}</td>`).join('')}</tr>`).join('')}
                        </tbody>
                    </table>
                    <script>window.print();</script>
                </body>
                </html>
            `);
        }
    } catch (e) {
        showToast("Error generating requested report", "error");
    }
}

// Utility: Number to Words conversion (Indian Currency context)
function numToWords(num) {
    const a = ['', 'One ', 'Two ', 'Three ', 'Four ', 'Five ', 'Six ', 'Seven ', 'Eight ', 'Nine ', 'Ten ', 'Eleven ', 'Twelve ', 'Thirteen ', 'Fourteen ', 'Fifteen ', 'Sixteen ', 'Seventeen ', 'Eighteen ', 'Nineteen '];
    const b = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];

    if ((num = num.toString()).length > 9) return 'overflow';
    let n = ('000000000' + num).substr(-9).match(/^(\d{2})(\d{2})(\d{2})(\d{1})(\d{2})$/);
    if (!n) return ''; 
    let str = '';
    str += (n[1] != 0) ? (a[Number(n[1])] || b[n[1][0]] + ' ' + a[n[1][1]]) + 'Crore ' : '';
    str += (n[2] != 0) ? (a[Number(n[2])] || b[n[2][0]] + ' ' + a[n[2][1]]) + 'Lakh ' : '';
    str += (n[3] != 0) ? (a[Number(n[3])] || b[n[3][0]] + ' ' + a[n[3][1]]) + 'Thousand ' : '';
    str += (n[4] != 0) ? (a[Number(n[4])] || b[n[4][0]] + ' ' + a[n[4][1]]) + 'Hundred ' : '';
    str += (n[5] != 0) ? ((str != '') ? 'and ' : '') + (a[Number(n[5])] || b[n[5][0]] + ' ' + a[n[5][1]]) : '';
    return str.trim();
}

function suggestEmail() {
    const name = document.getElementById('emp-name').value.trim();
    if (!name) {
        showToast("Please enter employee name first", "error");
        return;
    }
    const cleanName = name.toLowerCase().replace(/[^a-z0-9 ]/g, '').replace(/\s+/g, '.');
    const companyName = (document.getElementById('active-company-name').textContent || 'company').toLowerCase().replace(/\s+/g, '');
    document.getElementById('emp-email').value = `${cleanName}@${companyName || 'apex'}.com`;
    showToast("Corporate email suggested!", "info");
}

function suggestPassword() {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%";
    let pass = "";
    for (let i = 0; i < 10; i++) {
        pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    document.getElementById('emp-password').value = pass;
    document.getElementById('emp-password').type = 'text'; // temporarily show it
    showToast("Suggested secure password: " + pass, "info");
}

async function populateApprovingManagers() {
    try {
        const response = await fetch('/api/employees');
        const emps = await response.json();
        const select = document.getElementById('leave-approver-select');
        if (!select) return;
        select.innerHTML = '<option value="" disabled selected>Select Approver</option>';
        
        const managers = emps.filter(e => e.role !== 'Employee');
        managers.forEach(mgr => {
            const opt = document.createElement('option');
            opt.value = mgr.name;
            opt.textContent = `${mgr.name} (${mgr.role})`;
            select.appendChild(opt);
        });
    } catch (e) {
        showToast("Error loading approving managers", "error");
    }
}

// --- ENTERPRISE REPORT CENTER CONTROLLERS ---

let currentReportDomain = 'employees';

function switchReportDomain(domain, element) {
    currentReportDomain = domain;
    
    // Manage active tab style
    const tabs = document.querySelectorAll('#report-domain-list li');
    tabs.forEach(t => t.classList.remove('active-tab'));
    if (element) {
        element.classList.add('active-tab');
    }
    
    // Update Title Label
    const labels = {
        'employees': '👥 Employee Reports Registry',
        'payroll': '💰 Payroll Calculations & Summaries',
        'finance': '📊 Corporate Income & Expenses',
        'attendance': '📅 Daily Attendance Logs',
        'leaves': '🌴 Leave Balances & Approval Registry',
        'recruitment': '💼 Job Applications & Recruitment Pipeline',
        'inventory': '📦 Asset Stock & Warehouse Inventory',
        'vendor': '🤝 Vendor Profiles & Payments',
        'tax': '🧮 Professional Tax & TDS Contributions',
        'audit': '🛡️ Security Audits & Activity Trace',
        'ai': '🤖 Automated AI Generated Summary',
        'custom': '🛠️ Custom Selected Parameters Report'
    };
    document.getElementById('report-title-label').textContent = labels[domain] || 'Corporate Report Section';
    
    // Run preview automatically
    runReportPreview();
}

async function loadReportFiltersList() {
    try {
        const response = await fetch('/api/employees');
        const emps = await response.json();
        
        // Departments list
        const depts = [...new Set(emps.map(e => e.department).filter(Boolean))];
        const deptSelect = document.getElementById('filter-report-dept');
        deptSelect.innerHTML = '<option value="">All Departments</option>';
        depts.forEach(d => {
            deptSelect.innerHTML += `<option value="${d}">${d}</option>`;
        });
        
        // Employees list
        const empSelect = document.getElementById('filter-report-emp');
        empSelect.innerHTML = '<option value="">All Employees</option>';
        emps.forEach(e => {
            empSelect.innerHTML += `<option value="${e.id}">${e.name} (${e.employee_id_code})</option>`;
        });
    } catch (e) {
        console.error("Error loading report filters", e);
    }
}

async function runReportPreview() {
    const dept = document.getElementById('filter-report-dept').value;
    const emp = document.getElementById('filter-report-emp').value;
    const status = document.getElementById('filter-report-status').value;
    const start = document.getElementById('filter-report-start').value;
    const end = document.getElementById('filter-report-end').value;
    
    let url = `/api/reports/export?preview=true&type=${currentReportDomain}`;
    if (dept) url += `&department=${encodeURIComponent(dept)}`;
    if (emp) url += `&employee_id=${encodeURIComponent(emp)}`;
    if (status) url += `&status=${encodeURIComponent(status)}`;
    if (start) url += `&start_date=${encodeURIComponent(start)}`;
    if (end) url += `&end_date=${encodeURIComponent(end)}`;
    
    // Add month/year if payroll
    if (currentReportDomain === 'payroll') {
        const today = new Date();
        url += `&month=${today.getMonth() + 1}&year=${today.getFullYear()}`;
    }
    
    try {
        const head = document.getElementById('report-preview-head');
        const body = document.getElementById('report-preview-body');
        
        head.innerHTML = '<tr><th>Loading report rows...</th></tr>';
        body.innerHTML = '';
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            head.innerHTML = '<tr><th class="color-red">Access Validation Error</th></tr>';
            body.innerHTML = `<tr><td style="padding: 20px; color: var(--color-error); text-align: center;">${err.error || 'Access Denied.'}</td></tr>`;
            return;
        }
        
        const result = await response.json();
        
        // Generate header row
        if (!result.headers || result.headers.length === 0) {
            head.innerHTML = '<tr><th>No matching records found.</th></tr>';
            body.innerHTML = '<tr><td class="text-muted" style="text-align: center; padding: 20px;">No workspace data match the selected parameters.</td></tr>';
            return;
        }
        
        let headHTML = '<tr>';
        result.headers.forEach(h => {
            headHTML += `<th>${h}</th>`;
        });
        headHTML += '</tr>';
        head.innerHTML = headHTML;
        
        // Generate rows
        let bodyHTML = '';
        result.data.forEach(row => {
            bodyHTML += '<tr>';
            row.forEach(cell => {
                bodyHTML += `<td>${cell !== null ? cell : ''}</td>`;
            });
            bodyHTML += '</tr>';
        });
        body.innerHTML = bodyHTML;
        
    } catch (e) {
        showToast("Error loading report preview", "error");
    }
}

function exportReportFile(format) {
    const dept = document.getElementById('filter-report-dept').value;
    const emp = document.getElementById('filter-report-emp').value;
    const status = document.getElementById('filter-report-status').value;
    const start = document.getElementById('filter-report-start').value;
    const end = document.getElementById('filter-report-end').value;
    
    let url = `/api/reports/export?format=${format}&type=${currentReportDomain}`;
    if (dept) url += `&department=${encodeURIComponent(dept)}`;
    if (emp) url += `&employee_id=${encodeURIComponent(emp)}`;
    if (status) url += `&status=${encodeURIComponent(status)}`;
    if (start) url += `&start_date=${encodeURIComponent(start)}`;
    if (end) url += `&end_date=${encodeURIComponent(end)}`;
    
    if (currentReportDomain === 'payroll') {
        const today = new Date();
        url += `&month=${today.getMonth() + 1}&year=${today.getFullYear()}`;
    }
    
    // Redirect browser to trigger attachment download stream
    window.location.href = url;
    showToast(`Generating and exporting ${format.toUpperCase()} report...`, "success");
}

function printReportPreview() {
    const title = document.getElementById('report-title-label').textContent;
    const tableHead = document.getElementById('report-preview-head').outerHTML;
    const tableBody = document.getElementById('report-preview-body').outerHTML;
    
    const printWindow = window.open('', '_blank', 'width=900,height=600');
    printWindow.document.write(`
        <html>
        <head>
            <title>${title}</title>
            <style>
                body { font-family: 'Segoe UI', system-ui, sans-serif; padding: 30px; color: #1e293b; }
                h1 { font-size: 1.6rem; color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.85rem; }
                th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
                th { background-color: #f1f5f9; font-weight: 600; }
                .footer { margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 10px; font-size: 0.8rem; color: #64748b; text-align: right; }
            </style>
        </head>
        <body onload="window.print()">
            <h1>${title} - Enterprise Report Center</h1>
            <p><strong>Generated By:</strong> System Admin (Authorized Console)</p>
            <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            <table>
                ${tableHead}
                ${tableBody}
            </table>
            <div class="footer">CONFIDENTIAL - ENTERPRISEOS INTELLECTUAL PROPERTY</div>
        </body>
        </html>
    `);
    printWindow.document.close();
}

async function openReportEmailModal() {
    const email = prompt("Enter recipient email address:", "finance-manager@apex.com");
    if (!email) return;
    
    try {
        const response = await fetch('/api/reports/email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: currentReportDomain,
                email: email,
                format: 'pdf'
            })
        });
        const res = await response.json();
        showToast(res.message, "success");
    } catch (e) {
        showToast("Error emailing report", "error");
    }
}

async function backupReportToCloud() {
    try {
        const response = await fetch('/api/reports/cloud_backup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: currentReportDomain,
                format: 'pdf'
            })
        });
        const res = await response.json();
        showToast(res.message, "success");
    } catch (e) {
        showToast("Cloud backup sync error", "error");
    }
}

async function scheduleReportSubmit(event) {
    event.preventDefault();
    const freq = document.getElementById('schedule-frequency').value;
    const fmt = document.getElementById('schedule-format').value;
    const email = document.getElementById('schedule-email').value;
    
    try {
        const response = await fetch('/api/reports/schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                report_type: currentReportDomain,
                frequency: freq,
                format: fmt,
                recipient_email: email
            })
        });
        const res = await response.json();
        showToast(res.message, "success");
        document.getElementById('report-schedule-form').reset();
        loadScheduledReports();
    } catch (e) {
        showToast("Error scheduling report", "error");
    }
}

async function loadScheduledReports() {
    try {
        const response = await fetch('/api/reports/schedule');
        const schedules = await response.json();
        
        const body = document.getElementById('report-schedules-list-body');
        if (schedules.length === 0) {
            body.innerHTML = '<tr><td colspan="4" class="text-muted" style="text-align: center; padding: 10px;">No automated summaries scheduled.</td></tr>';
            return;
        }
        
        let html = '';
        schedules.forEach(s => {
            html += `
                <tr>
                    <td style="font-weight: 600;">${s.report_type.toUpperCase()}</td>
                    <td>${s.frequency}</td>
                    <td><span class="badge badge-outline">${s.format.toUpperCase()}</span></td>
                    <td>${s.recipient_email}</td>
                </tr>
            `;
        });
        body.innerHTML = html;
    } catch (e) {
        console.error("Error loading schedules", e);
    }
}

