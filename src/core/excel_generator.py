"""
Excel Project Management Workbook Generator

Creates multi-sheet Excel workbooks for project management with
formatted headers, sample data, and automatic column sizing.

Usage:
    from src.core.excel_generator import create_project_management_workbook
    create_project_management_workbook('output.xlsx')
"""

from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

# Constants for sample data
INITIAL_BUDGET = 10000
OFFICE_SUPPLIES_EXPENSE = 500
REMAINING_BALANCE = 9500
OFFICE_SUPPLIES_BUDGET = 2000
MARKETING_BUDGET = 5000
DEVELOPMENT_BUDGET = 3000


def _apply_header_style(sheet: Worksheet, headers: list[str], fill_color: str = "CCE5FF") -> None:
    """
    Apply consistent header styling to a worksheet.

    Args:
        sheet: Worksheet to style
        headers: List of header column names
        fill_color: Hex color code for header background
    """
    for column_index, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=column_index)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")


def _auto_size_columns(workbook: Workbook) -> None:
    """
    Auto-size all columns in all sheets of a workbook.

    Args:
        workbook: Workbook to adjust
    """
    for sheet in workbook.worksheets:
        for column_index in range(1, sheet.max_column + 1):
            sheet.column_dimensions[get_column_letter(column_index)].width = 15


def create_project_management_workbook(filename: str | None = None) -> Workbook:
    """
    Create a project management Excel workbook with formatted sheets.

    Args:
        filename: Output filename (defaults to 'Project_Management.xlsx')

    Returns:
        Created workbook object

    Sheets:
        - Financial Transactions: Budget tracking with income/expense
        - Project Tasks: Task management with assignments and deadlines
        - Budget Summary: Category-wise budget allocation and spending
    """
    if filename is None:
        filename = "Project_Management.xlsx"

    # Create a new workbook
    workbook = openpyxl.Workbook()

    # Financial Transactions Sheet
    transactions_sheet = workbook.active
    transactions_sheet.title = "Financial Transactions"
    trans_headers = ["Date", "Description", "Category", "Income", "Expense", "Balance"]
    _apply_header_style(transactions_sheet, trans_headers, "CCE5FF")

    # Project Tasks Sheet
    tasks_sheet = workbook.create_sheet(title="Project Tasks")
    task_headers = ["Task ID", "Task Name", "Start Date", "Due Date", "Status", "Assigned To", "Notes"]
    _apply_header_style(tasks_sheet, task_headers, "E6FFE6")

    # Budget Summary Sheet
    budget_sheet = workbook.create_sheet(title="Budget Summary")
    budget_headers = ["Category", "Budgeted", "Spent", "Remaining", "Percent Spent"]
    _apply_header_style(budget_sheet, budget_headers, "FFE6CC")
    # Auto-size columns for all sheets
    _auto_size_columns(workbook)

    # Sample transactions
    sample_transactions = [
        [datetime.now().strftime("%Y-%m-%d"), "Initial Budget", "Budget", INITIAL_BUDGET, 0, INITIAL_BUDGET],
        [
            datetime.now().strftime("%Y-%m-%d"),
            "Office Supplies",
            "Expenses",
            0,
            OFFICE_SUPPLIES_EXPENSE,
            REMAINING_BALANCE,
        ],
    ]

    # Add sample data to sheets
    # Transactions
    for row, data in enumerate(sample_transactions, 2):
        for column_index, value in enumerate(data, 1):
            transactions_sheet.cell(row=row, column=column_index).value = value

    # Tasks
    sample_tasks = [
        [
            1,
            "Design",
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d"),
            "In Progress",
            "Alice",
            "",
        ],
        [
            2,
            "Development",
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d"),
            "Not Started",
            "Bob",
            "",
        ],
    ]
    for row, data in enumerate(sample_tasks, 2):
        for column_index, value in enumerate(data, 1):
            tasks_sheet.cell(row=row, column=column_index).value = value

    # Budget Categories
    sample_budget = [
        ["Office Supplies", OFFICE_SUPPLIES_BUDGET, OFFICE_SUPPLIES_EXPENSE, "=B2-C2", "=C2/B2*100"],
        ["Marketing", MARKETING_BUDGET, 0, "=B3-C3", "=C3/B3*100"],
        ["Development", DEVELOPMENT_BUDGET, 0, "=B4-C4", "=C4/B4*100"],
    ]
    for row, data in enumerate(sample_budget, 2):
        for column_index, value in enumerate(data, 1):
            budget_sheet.cell(row=row, column=column_index).value = value

    # Save the workbook
    workbook.save(filename)
    return workbook


# Example usage:
# create_project_management_workbook('Project_Management.xlsx')
