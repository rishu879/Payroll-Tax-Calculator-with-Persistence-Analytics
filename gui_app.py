"""
gui_app.py
----------
SQLite Payroll Management System — Desktop GUI (CustomTkinter)

A data-analyst style desktop tool for a small business:
  - Employees tab   : add/view/delete staff and their computed pay
  - Expenses tab     : add/view/delete company expenses
  - Revenue tab      : add/view/delete income entries
  - Dashboard tab     : SQL-driven KPIs (total wages, expenses, revenue,
                        net profit) + a live matplotlib chart, filterable
                        by month.

All SQL lives in database.py — this file is purely presentation logic.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import PayrollDB
import export as export_module

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CURRENCY = "$"  # change to "Rs " / "€" / etc. if needed


def fmt_money(value):
    return f"{CURRENCY}{value:,.2f}"


class PayrollApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = PayrollDB()

        self.title("Payroll Management System")
        self.geometry("1050x680")
        self.minsize(900, 600)

        # ---- layout: a tabview holding the four sections ----
        self.tabview = ctk.CTkTabview(self, width=1000, height=640)
        self.tabview.pack(padx=15, pady=15, fill="both", expand=True)

        self.tab_employees = self.tabview.add("Employees")
        self.tab_expenses = self.tabview.add("Expenses")
        self.tab_revenue = self.tabview.add("Revenue")
        self.tab_dashboard = self.tabview.add("Dashboard")

        self.build_employees_tab()
        self.build_expenses_tab()
        self.build_revenue_tab()
        self.build_dashboard_tab()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ======================================================================
    # EMPLOYEES TAB
    # ======================================================================
    def build_employees_tab(self):
        frame = self.tab_employees

        form = ctk.CTkFrame(frame)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.emp_name = ctk.CTkEntry(form, width=160)
        self.emp_name.grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkLabel(form, text="Position").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.emp_position = ctk.CTkEntry(form, width=140)
        self.emp_position.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Pay Type").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.emp_pay_type = ctk.CTkOptionMenu(form, values=["Salary", "Hourly"],
                                               command=self.toggle_hours_field, width=110)
        self.emp_pay_type.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkLabel(form, text="Rate ($)").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.emp_rate = ctk.CTkEntry(form, width=100)
        self.emp_rate.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(form, text="Hours").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.emp_hours = ctk.CTkEntry(form, width=80)
        self.emp_hours.grid(row=1, column=4, padx=5, pady=5)
        self.emp_hours.configure(state="disabled")

        ctk.CTkLabel(form, text="Pay Month (YYYY-MM)").grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.emp_month = ctk.CTkEntry(form, width=110)
        self.emp_month.insert(0, datetime.now().strftime("%Y-%m"))
        self.emp_month.grid(row=1, column=5, padx=5, pady=5)

        ctk.CTkButton(form, text="Add Employee", command=self.add_employee).grid(
            row=1, column=6, padx=10, pady=5)

        # ---- table ----
        columns = ("ID", "Name", "Position", "Pay Type", "Rate", "Hours", "Month", "Gross Pay")
        self.emp_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=110, anchor="center")
        self.emp_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=(0, 10))
        ctk.CTkButton(btn_row, text="Delete Selected", fg_color="#b03030",
                      hover_color="#8a2424", command=self.delete_employee).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Export to CSV", command=self.export_employees).pack(side="left", padx=5)

        self.refresh_employees()

    def toggle_hours_field(self, choice):
        if choice == "Hourly":
            self.emp_hours.configure(state="normal")
        else:
            self.emp_hours.delete(0, "end")
            self.emp_hours.configure(state="disabled")

    def add_employee(self):
        try:
            name = self.emp_name.get().strip()
            position = self.emp_position.get().strip()
            pay_type = self.emp_pay_type.get()
            rate = float(self.emp_rate.get())
            hours = float(self.emp_hours.get()) if pay_type == "Hourly" and self.emp_hours.get() else 0
            month = self.emp_month.get().strip()

            if not name or not month:
                raise ValueError("Name and Pay Month are required.")
            datetime.strptime(month, "%Y-%m")  # validates format

            self.db.add_employee(name, position, pay_type, rate, hours, month)
            self.refresh_employees()
            self.refresh_dashboard()
            self.emp_name.delete(0, "end")
            self.emp_position.delete(0, "end")
            self.emp_rate.delete(0, "end")
            self.emp_hours.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Please check your entries.\n({e})")

    def refresh_employees(self):
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        for row in self.db.get_employees():
            emp_id, name, position, pay_type, rate, hours, month, gross = row
            self.emp_tree.insert("", "end", values=(
                emp_id, name, position, pay_type, fmt_money(rate),
                hours if pay_type == "Hourly" else "-", month, fmt_money(gross)
            ))

    def delete_employee(self):
        selected = self.emp_tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select an employee row to delete.")
            return
        emp_id = self.emp_tree.item(selected[0])["values"][0]
        self.db.delete_employee(emp_id)
        self.refresh_employees()
        self.refresh_dashboard()

    def export_employees(self):
        rows = self.db.get_employees()
        if not rows:
            messagebox.showinfo("Nothing to export", "There are no employee records yet.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile="employees_export.csv")
        if filepath:
            export_module.export_employees_csv(rows, filepath)
            messagebox.showinfo("Export complete", f"Employees exported to:\n{filepath}")

    # ======================================================================
    # EXPENSES TAB
    # ======================================================================
    def build_expenses_tab(self):
        frame = self.tab_expenses

        form = ctk.CTkFrame(frame)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Category").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.exp_category = ctk.CTkOptionMenu(
            form, values=["Rent", "Utilities", "Supplies", "Marketing", "Maintenance", "Other"])
        self.exp_category.grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkLabel(form, text="Description").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.exp_description = ctk.CTkEntry(form, width=220)
        self.exp_description.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Amount ($)").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.exp_amount = ctk.CTkEntry(form, width=100)
        self.exp_amount.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.exp_date = ctk.CTkEntry(form, width=120)
        self.exp_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.exp_date.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkButton(form, text="Add Expense", command=self.add_expense).grid(
            row=1, column=4, padx=10, pady=5)

        columns = ("ID", "Category", "Description", "Amount", "Date")
        self.exp_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.exp_tree.heading(col, text=col)
            self.exp_tree.column(col, width=140, anchor="center")
        self.exp_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=(0, 10))
        ctk.CTkButton(btn_row, text="Delete Selected", fg_color="#b03030",
                      hover_color="#8a2424", command=self.delete_expense).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Export to CSV", command=self.export_expenses).pack(side="left", padx=5)

        self.refresh_expenses()

    def add_expense(self):
        try:
            category = self.exp_category.get()
            description = self.exp_description.get().strip()
            amount = float(self.exp_amount.get())
            date_str = self.exp_date.get().strip()
            datetime.strptime(date_str, "%Y-%m-%d")

            self.db.add_expense(category, description, amount, date_str)
            self.refresh_expenses()
            self.refresh_dashboard()
            self.exp_description.delete(0, "end")
            self.exp_amount.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Please check your entries.\n({e})")

    def refresh_expenses(self):
        for row in self.exp_tree.get_children():
            self.exp_tree.delete(row)
        for row in self.db.get_expenses():
            exp_id, category, description, amount, exp_date = row
            self.exp_tree.insert("", "end", values=(exp_id, category, description, fmt_money(amount), exp_date))

    def delete_expense(self):
        selected = self.exp_tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select an expense row to delete.")
            return
        exp_id = self.exp_tree.item(selected[0])["values"][0]
        self.db.delete_expense(exp_id)
        self.refresh_expenses()
        self.refresh_dashboard()

    def export_expenses(self):
        rows = self.db.get_expenses()
        if not rows:
            messagebox.showinfo("Nothing to export", "There are no expense records yet.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile="expenses_export.csv")
        if filepath:
            export_module.export_expenses_csv(rows, filepath)
            messagebox.showinfo("Export complete", f"Expenses exported to:\n{filepath}")

    # ======================================================================
    # REVENUE TAB
    # ======================================================================
    def build_revenue_tab(self):
        frame = self.tab_revenue

        form = ctk.CTkFrame(frame)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Source").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.rev_source = ctk.CTkEntry(form, width=200)
        self.rev_source.grid(row=1, column=0, padx=5, pady=5)

        ctk.CTkLabel(form, text="Amount ($)").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.rev_amount = ctk.CTkEntry(form, width=120)
        self.rev_amount.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.rev_date = ctk.CTkEntry(form, width=120)
        self.rev_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.rev_date.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(form, text="Add Revenue", command=self.add_revenue).grid(
            row=1, column=3, padx=10, pady=5)

        columns = ("ID", "Source", "Amount", "Date")
        self.rev_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.rev_tree.heading(col, text=col)
            self.rev_tree.column(col, width=160, anchor="center")
        self.rev_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=(0, 10))
        ctk.CTkButton(btn_row, text="Delete Selected", fg_color="#b03030",
                      hover_color="#8a2424", command=self.delete_revenue).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Export to CSV", command=self.export_revenue).pack(side="left", padx=5)

        self.refresh_revenue()

    def add_revenue(self):
        try:
            source = self.rev_source.get().strip()
            amount = float(self.rev_amount.get())
            date_str = self.rev_date.get().strip()
            datetime.strptime(date_str, "%Y-%m-%d")
            if not source:
                raise ValueError("Source is required.")

            self.db.add_revenue(source, amount, date_str)
            self.refresh_revenue()
            self.refresh_dashboard()
            self.rev_source.delete(0, "end")
            self.rev_amount.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Please check your entries.\n({e})")

    def refresh_revenue(self):
        for row in self.rev_tree.get_children():
            self.rev_tree.delete(row)
        for row in self.db.get_revenue():
            rev_id, source, amount, rev_date = row
            self.rev_tree.insert("", "end", values=(rev_id, source, fmt_money(amount), rev_date))

    def delete_revenue(self):
        selected = self.rev_tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a revenue row to delete.")
            return
        rev_id = self.rev_tree.item(selected[0])["values"][0]
        self.db.delete_revenue(rev_id)
        self.refresh_revenue()
        self.refresh_dashboard()

    def export_revenue(self):
        rows = self.db.get_revenue()
        if not rows:
            messagebox.showinfo("Nothing to export", "There are no revenue records yet.")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile="revenue_export.csv")
        if filepath:
            export_module.export_revenue_csv(rows, filepath)
            messagebox.showinfo("Export complete", f"Revenue exported to:\n{filepath}")

    # ======================================================================
    # DASHBOARD TAB
    # ======================================================================
    def build_dashboard_tab(self):
        frame = self.tab_dashboard

        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="Filter by month:").pack(side="left", padx=(5, 5))
        self.month_filter = ctk.CTkOptionMenu(top, values=["All Time"], command=lambda _: self.refresh_dashboard())
        self.month_filter.pack(side="left", padx=5)
        ctk.CTkButton(top, text="Refresh", command=self.refresh_dashboard).pack(side="left", padx=10)
        ctk.CTkButton(top, text="Export Report to CSV", command=self.export_summary).pack(side="left", padx=10)

        # KPI cards
        cards = ctk.CTkFrame(frame)
        cards.pack(fill="x", padx=10, pady=10)

        self.card_revenue = self.make_kpi_card(cards, "Total Revenue", 0)
        self.card_wages = self.make_kpi_card(cards, "Total Wages", 1)
        self.card_expenses = self.make_kpi_card(cards, "Total Expenses", 2)
        self.card_profit = self.make_kpi_card(cards, "Net Profit", 3)

        # Chart
        chart_frame = ctk.CTkFrame(frame)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(9, 4.2), dpi=100)
        self.ax_bar = self.figure.add_subplot(1, 2, 1)
        self.ax_pie = self.figure.add_subplot(1, 2, 2)
        self.figure.patch.set_facecolor("#2b2b2b")

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.refresh_dashboard()

    def make_kpi_card(self, parent, title, col):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13)).pack(pady=(10, 2))
        value_label = ctk.CTkLabel(card, text="$0.00", font=ctk.CTkFont(size=22, weight="bold"))
        value_label.pack(pady=(0, 10))
        return value_label

    def refresh_dashboard(self):
        # keep month dropdown in sync with whatever data exists
        months = self.db.get_available_months()
        options = ["All Time"] + months
        current = self.month_filter.get()
        self.month_filter.configure(values=options)
        if current not in options:
            self.month_filter.set("All Time")
            current = "All Time"

        month = None if current == "All Time" else current

        revenue = self.db.get_total_revenue(month)
        wages = self.db.get_total_wages(month)
        expenses = self.db.get_total_expenses(month)
        profit = revenue - wages - expenses

        self.card_revenue.configure(text=fmt_money(revenue))
        self.card_wages.configure(text=fmt_money(wages))
        self.card_expenses.configure(text=fmt_money(expenses))
        self.card_profit.configure(
            text=fmt_money(profit),
            text_color="#4caf50" if profit >= 0 else "#e53935"
        )

        self.update_charts(month, revenue, wages, expenses)

    def update_charts(self, month, revenue, wages, expenses):
        self.ax_bar.clear()
        self.ax_pie.clear()

        # Bar chart: revenue vs wages vs expenses
        labels = ["Revenue", "Wages", "Expenses"]
        values = [revenue, wages, expenses]
        colors = ["#4caf50", "#42a5f5", "#e57373"]
        self.ax_bar.bar(labels, values, color=colors)
        self.ax_bar.set_title("Revenue vs Wages vs Expenses", color="white", fontsize=10)
        self.ax_bar.tick_params(colors="white")
        self.ax_bar.set_facecolor("#2b2b2b")
        for spine in self.ax_bar.spines.values():
            spine.set_color("white")

        # Pie chart: expense breakdown by category
        breakdown = self.db.get_expense_breakdown(month)
        if breakdown:
            cats = [b[0] for b in breakdown]
            amounts = [b[1] for b in breakdown]
            self.ax_pie.pie(amounts, labels=cats, autopct="%1.0f%%",
                             textprops={"color": "white", "fontsize": 8})
        else:
            self.ax_pie.text(0.5, 0.5, "No expense data", ha="center", va="center", color="white")
        self.ax_pie.set_title("Expense Breakdown", color="white", fontsize=10)
        self.figure.patch.set_facecolor("#2b2b2b")

        self.canvas.draw()

    def export_summary(self):
        month_label = self.month_filter.get()
        month = None if month_label == "All Time" else month_label

        revenue = self.db.get_total_revenue(month)
        wages = self.db.get_total_wages(month)
        expenses = self.db.get_total_expenses(month)
        profit = revenue - wages - expenses
        breakdown = self.db.get_expense_breakdown(month)

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            initialfile=f"payroll_summary_{month_label.replace(' ', '_')}.csv")
        if filepath:
            export_module.export_summary_csv(month_label, revenue, wages, expenses, profit, breakdown, filepath)
            messagebox.showinfo("Export complete", f"Summary report exported to:\n{filepath}")

    # ======================================================================
    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = PayrollApp()
    app.mainloop()
