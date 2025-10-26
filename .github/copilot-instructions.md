# Copilot Instructions

## Project Overview
This is a comprehensive financial and data analysis system built with Python, serving Rahman Finance and Accounting P.L.LLC. The system encompasses both operational business tools and academic data science projects from WGU MBA coursework.

### Primary Components
1. **Financial Data Management**: Excel workbook creation and manipulation for business operations
2. **Data Science & Analysis Projects**: Business analysis, SWOT analysis, and investigation techniques from MBA coursework
3. **SharePoint Integration**: Permission and access management for collaborative academic and business documents

## Core Architecture

### Main Components
- **Financial Data Management**: Built around `openpyxl` for Excel workbook creation and manipulation
- **Data Science Pipeline**: Academic analysis projects focusing on business intelligence and strategic analysis
- **Multi-Sheet Structure**: Creates workbooks with three distinct sheets for different business functions:
  - Financial Transactions (blue headers: `CCE5FF`)
  - Project Tasks (green headers: `E6FFE6`) 
  - Budget Summary (orange headers: `FFE6CC`)

### Key Files
- `src/core/excel_generator.py`: Main workbook generator script (previously MyProject/create_project_workbook.py)
- `data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv`: SharePoint permissions data
- `output/reports/financial/Project_Management.xlsx`: Generated financial workbook
- `config/paths.json`: File path configurations

## Development Patterns

### Excel Workbook Creation Pattern
```python
# Standard sheet creation pattern used throughout
sheet = wb.create_sheet(title="Sheet Name")
headers = ["Col1", "Col2", "Col3"]
for col, header in enumerate(headers, 1):
    cell = sheet.cell(row=1, column=col)
    cell.value = header
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="COLOR", end_color="COLOR", fill_type="solid")
```

### Data Structure Conventions
- **Financial transactions**: Date (YYYY-MM-DD), Description, Category, Income, Expense, Balance
- **Project tasks**: Task ID (numeric), Name, Start Date, Due Date, Status, Assigned To, Notes
- **Budget categories**: Category, Budgeted Amount, Actual Amount, Variance (formula), % Used (formula)

### Styling Standards
- Column width: Fixed at 15 units for all sheets
- Header styling: Bold font with color-coded backgrounds
- Formula usage: Excel formulas for calculated fields (variance, percentages)

## Data Flow
1. Create workbook instance with `openpyxl.Workbook()`
2. Configure active sheet as Financial Transactions
3. Add Project Tasks and Budget Summary sheets
4. Apply consistent formatting across all sheets
5. Populate with sample data for immediate usability
6. Save as `Project_Management.xlsx`

## External Data Source Integration

### Current Data Sources
- **SharePoint/OneDrive permissions data**: CSV exports from Microsoft 365 with permission structures
  - File pattern: `Hassan Rahman_YYYY-M-DD-HH-MM-S_N.csv`
  - Contains: Resource Path, Item Type, Permission, User Name, User Email, User Or Group Type, Link ID, Link Type, AccessViaLinkID

### Data Integration Patterns
The codebase follows a structured approach for integrating external data:

#### Sample Data Structure Pattern
```python
# Current pattern: Static sample data arrays
sample_trans = [
    [datetime.now().strftime("%Y-%m-%d"), "Description", "Category", income, expense, balance],
    # Additional rows...
]
```

#### Recommended External Data Integration
For CSV data integration, extend the existing pattern:
```python
import csv

def load_transaction_data(csv_file_path):
    """Load financial data from CSV file following existing structure"""
    transactions = []
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Map CSV columns to workbook structure
            transactions.append([
                row['Date'], row['Description'], row['Category'],
                float(row.get('Income', 0)), float(row.get('Expense', 0)),
                float(row.get('Balance', 0))
            ])
    return transactions
```

#### SharePoint Data Integration
For OneDrive/SharePoint permission data:
```python
def process_sharepoint_permissions(csv_file_path):
    """Process SharePoint permissions data for compliance tracking"""
    permissions = []
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            permissions.append([
                row['Resource Path'], row['User Name'], row['Permission'],
                row['User Email'], row['User Or Group Type']
            ])
    return permissions
```

### Data Validation Standards
- **Date formats**: Use ISO format (YYYY-MM-DD) for consistency
- **Numeric fields**: Validate and convert to appropriate types (int/float)
- **Text normalization**: Strip whitespace and handle encoding issues
- **Missing data**: Provide sensible defaults (0 for numeric, empty string for text)

## Data Science & Business Analysis Projects

### Academic Analysis Framework
The system supports various business analysis methodologies from WGU MBA coursework:

#### SWOT Analysis Components
- **Strategic Analysis**: Cisco Systems SWOT, HCL Technologies SWOT analysis
- **Investigation Techniques**: Business analysis methodologies and frameworks
- **Project Management Analysis**: Task 3 Analysis workflows with Excel-based reporting

#### Analysis File Patterns
```python
def create_swot_analysis_sheet(workbook, company_name):
    """Create SWOT analysis sheet for strategic business analysis"""
    swot_sheet = workbook.create_sheet(title=f"SWOT - {company_name}")
    swot_headers = ["Category", "Strengths", "Weaknesses", "Opportunities", "Threats", "Strategic Impact"]
    
    # Apply academic formatting standards
    for col, header in enumerate(swot_headers, 1):
        cell = swot_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="D4E6F1", end_color="D4E6F1", fill_type="solid")
    
    return swot_sheet

def create_project_analysis_workbook(project_name, analysis_type="strategic"):
    """Generate comprehensive project analysis workbook for MBA coursework"""
    wb = openpyxl.Workbook()
    
    # Create analysis-specific sheets
    if analysis_type == "strategic":
        create_swot_analysis_sheet(wb, project_name)
    elif analysis_type == "project_management":
        create_task_analysis_sheet(wb, project_name)
    
    return wb
```

#### WGU MBA Integration Points
- **Course Structure**: Organized by course codes and sequence numbers
  - `04 C212 Marketing`: Marketing fundamentals with Pride-Ferrell textbook chapters
  - `06 MMG2`: Strategic management with SWOT analysis methodologies  
  - `07 Project Management`: Task analysis and project management frameworks
  - `10 C207`: Data-driven decision making and business analytics (advanced data science course)
- **Document Management**: PDF references, Excel analysis files, collaborative sharing
- **Analysis Workflows**: Investigation techniques, strategic analysis, project management methodologies, quantitative business analytics

#### C207 Data Science Course Integration
```python
def create_analytics_dashboard(dataset_name, analysis_type="descriptive"):
    """Generate data science analysis workbook for C207 coursework"""
    wb = openpyxl.Workbook()
    
    # Create analytics-specific sheets
    if analysis_type == "descriptive":
        create_descriptive_analytics_sheet(wb, dataset_name)
    elif analysis_type == "predictive":
        create_predictive_modeling_sheet(wb, dataset_name)
    elif analysis_type == "prescriptive":
        create_optimization_sheet(wb, dataset_name)
    
    # Add data visualization summary sheet
    create_visualization_summary_sheet(wb, dataset_name)
    
    return wb

def create_descriptive_analytics_sheet(workbook, dataset_name):
    """Create descriptive analytics sheet for C207 data analysis"""
    analytics_sheet = workbook.create_sheet(title=f"Analytics - {dataset_name}")
    analytics_headers = [
        "Variable", "Data Type", "Mean", "Median", "Std Dev", 
        "Min", "Max", "Missing Values", "Insights"
    ]
    
    # Apply data science formatting standards
    for col, header in enumerate(analytics_headers, 1):
        cell = analytics_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="B8860B", end_color="B8860B", fill_type="solid")  # Gold for data science
    
    return analytics_sheet
```

### Data Science Workflow (C207 Course)
The C207 course focuses on advanced business analytics and data-driven decision making:

#### Typical Data Science Project Structure
```python
# Standard data science imports for C207 projects
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import openpyxl
from openpyxl.chart import BarChart, Reference, LineChart

def c207_data_analysis_pipeline(data_file, output_name):
    """Complete data analysis pipeline for C207 coursework"""
    
    # 1. Data Loading and Cleaning
    df = pd.read_csv(data_file)
    cleaned_df = clean_dataset(df)
    
    # 2. Descriptive Analytics
    descriptive_stats = perform_descriptive_analysis(cleaned_df)
    
    # 3. Create Excel workbook with multiple analysis sheets
    wb = create_analytics_dashboard(output_name, "descriptive")
    
    # 4. Add statistical analysis
    add_statistical_tests(wb, cleaned_df)
    
    # 5. Generate visualizations
    create_business_charts(wb, cleaned_df)
    
    wb.save(f'C207_{output_name}_Analysis.xlsx')
    return wb

def clean_dataset(df):
    """Data cleaning following C207 best practices"""
    # Handle missing values
    df_cleaned = df.dropna(thresh=len(df.columns) * 0.7)  # Remove rows with >30% missing
    
    # Standardize data types
    for col in df_cleaned.select_dtypes(include=['object']):
        if df_cleaned[col].str.contains(r'^\d+\.?\d*$', na=False).all():
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
    
    return df_cleaned

def add_statistical_tests(workbook, dataframe):
    """Add statistical analysis sheets for hypothesis testing"""
    stats_sheet = workbook.create_sheet(title="Statistical Tests")
    
    # Add headers for statistical analysis
    stats_headers = ["Test Type", "Variables", "P-Value", "Result", "Business Implication"]
    for col, header in enumerate(stats_headers, 1):
        cell = stats_sheet.cell(row=1, column=col)
        cell.value = header
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")  # Green for statistics
```

#### Data Science Dependencies (C207 Extended)
```python
# Additional dependencies for advanced analytics
import pandas as pd          # Data manipulation and analysis
import numpy as np           # Numerical computing
import matplotlib.pyplot as plt  # Data visualization
import seaborn as sns        # Statistical data visualization
import scipy.stats as stats  # Statistical functions
import sklearn               # Machine learning (if predictive analysis required)
```

## Dependencies
- `openpyxl`: Excel file manipulation (styles, utils, core workbook functions)
- `datetime`: For current date formatting in financial transactions
- `csv`: For external data source integration (built-in Python module)
- `pandas`: Data manipulation and analysis (C207 data science projects)
- `numpy`: Numerical computing for statistical analysis
- `matplotlib/seaborn`: Data visualization for business analytics

## Running the Project
Execute the main script from the organized structure:
```bash
python src/core/excel_generator.py
```
This generates a ready-to-use Excel workbook in `output/reports/financial/`

For data processing workflows:
```bash
# Process SharePoint permissions data
python src/integrations/sharepoint_connector.py

# Run C207 analytics
python src/analytics/c207_workflows.py

# Generate SWOT analysis
python src/business/swot_analyzer.py
```

## Business Context
This tool serves Rahman Finance and Accounting P.L.LLC's need for standardized project management and financial tracking templates, as well as supporting academic data science and business analysis projects from WGU MBA coursework. The generated workbooks provide immediate structure for:
- Transaction logging with automatic balance tracking
- Project task management with status and assignment tracking
- Budget monitoring with variance calculations
- Strategic business analysis (SWOT, competitive analysis)
- Academic project management analysis and reporting
- Investigation techniques and business intelligence workflows