import csv

def export_employees_csv(rows, filepath):
    headers = ["ID", "Name", "Position", "Pay Type", "Rate", "Hours", "Month", "Gross Pay"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def export_expenses_csv(rows, filepath):
    headers = ["ID", "Category", "Description", "Amount", "Date"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def export_revenue_csv(rows, filepath):
    headers = ["ID", "Source", "Amount", "Date"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def export_summary_csv(month_label, revenue, wages, expenses, profit, breakdown, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["PAYROLL AND FINANCE SUMMARY", month_label])
        writer.writerow([])
        writer.writerow(["KPI METRICS"])
        writer.writerow(["Total Revenue", f"${revenue:,.2f}"])
        writer.writerow(["Total Wages", f"${wages:,.2f}"])
        writer.writerow(["Total Expenses", f"${expenses:,.2f}"])
        writer.writerow(["Net Profit", f"${profit:,.2f}"])
        writer.writerow([])
        writer.writerow(["EXPENSE BREAKDOWN BY CATEGORY"])
        writer.writerow(["Category", "Amount"])
        for cat, amt in breakdown:
            writer.writerow([cat, f"${amt:,.2f}"])
