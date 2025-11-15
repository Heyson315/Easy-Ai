from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

# Constants for sample data
INITIAL_BUDGET = 10000
OFFICE_SUPPLIES_EXPENSE = 500
REMAINING_BALANCE = 9500
OFFICE_SUPPLIES_BUDGET = 2000
MARKETING_BUDGET = 5000
DEVELOPMENT_BUDGET = 3000


def create_project_management_workbook(filename=None):
    """
    Create a project management Excel workbook.

    Args:
        filename (str, optional): Output filename for the workbook. Defaults to 'Project_Management.xlsx'.
        
    Returns:
        openpyxl.Workbook: The created workbook object
        
    Raises:
        PermissionError: If the file cannot be written (e.g., file is open)
        ValueError: If filename is invalid
    """
    if filename is None:
        filename = "Project_Management.xlsx"
    
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # Create a new workbook
    wb = openpyxl.Workbook()

    # Financial Transactions Sheet
    trans_sheet = wb.active
    trans_sheet.title = "Financial Transactions"
    trans_headers = ["Date", "Description", "Category", "Income", "Expense", "Balance"]
    for col, header in enumerate(trans_headers, 1):
        cell = trans_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

    # Project Tasks Sheet
    task_sheet = wb.create_sheet(title="Project Tasks")
    task_headers = ["Task ID", "Task Name", "Start Date", "Due Date", "Status", "Assigned To", "Notes"]
    for col, header in enumerate(task_headers, 1):
        cell = task_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="E6FFE6", end_color="E6FFE6", fill_type="solid")

    # Budget Summary Sheet
    budget_sheet = wb.create_sheet(title="Budget Summary")
    budget_headers = ["Category", "Budgeted", "Spent", "Remaining", "Percent Spent"]
    for col, header in enumerate(budget_headers, 1):
        cell = budget_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="FFE6CC", end_color="FFE6CC", fill_type="solid")

    # Adjust column widths for all sheets
    for sheet in wb.worksheets:
        for col in range(1, sheet.max_column + 1):
            sheet.column_dimensions[get_column_letter(col)].width = 15

    # Sample transactions
    sample_trans = [
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

    # Add sample data
    # Transactions
    for row, data in enumerate(sample_trans, 2):
        for col, value in enumerate(data, 1):
            trans_sheet.cell(row=row, column=col).value = value

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
        for col, value in enumerate(data, 1):
            task_sheet.cell(row=row, column=col).value = value

    # Budget Categories
    sample_budget = [
        ["Office Supplies", OFFICE_SUPPLIES_BUDGET, OFFICE_SUPPLIES_EXPENSE, "=B2-C2", "=C2/B2*100"],
        ["Marketing", MARKETING_BUDGET, 0, "=B3-C3", "=C3/B3*100"],
        ["Development", DEVELOPMENT_BUDGET, 0, "=B4-C4", "=C4/B4*100"],
    ]
    for row, data in enumerate(sample_budget, 2):
        for col, value in enumerate(data, 1):
            budget_sheet.cell(row=row, column=col).value = value

    # Save the workbook
    try:
        wb.save(filename)
        print(f"✓ Workbook created successfully: {filename}")
    except PermissionError as e:
        raise PermissionError(
            f"Cannot write to {filename}. Please close the file if it's open."
        ) from e
    except OSError as e:
        raise OSError(f"OS error writing to {filename}: {e}") from e
    except ValueError as e:
        raise ValueError(f"Invalid data for Excel: {e}") from e
    
    return wb


# Example usage:
# create_project_management_workbook('Project_Management.xlsx')
