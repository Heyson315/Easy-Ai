#!/usr/bin/env python3
"""
Setup script to create optimal directory structure for Rahman Analytics Hub
Run this script to automatically create the recommended file organization
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the recommended directory structure"""
    
    # Define the directory structure
    directories = [
        # Core structure
        "src/core",
        "src/financial", 
        "src/analytics",
        "src/business",
        "src/academic", 
        "src/integrations",
        
        # Data organization
        "data/raw/sharepoint",
        "data/raw/financial",
        "data/raw/academic/c207_datasets",
        "data/raw/academic/c212_market_data", 
        "data/raw/academic/project_data",
        "data/processed",
        "data/external",
        "data/archive",
        
        # Output organization
        "output/reports/financial",
        "output/reports/academic/c207_analysis",
        "output/reports/academic/swot_reports", 
        "output/reports/academic/project_reports",
        "output/reports/business/client_deliverables",
        "output/reports/business/internal_reports",
        "output/dashboards",
        "output/presentations",
        "output/automated/daily",
        "output/automated/weekly",
        "output/automated/monthly",
        
        # Templates
        "templates/excel",
        "templates/python", 
        "templates/academic",
        
        # Supporting directories
        "docs",
        "tests",
        "config",
        "scripts"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files for Python packages
    python_packages = [
        "src",
        "src/core",
        "src/financial",
        "src/analytics", 
        "src/business",
        "src/academic",
        "src/integrations"
    ]
    
    for package in python_packages:
        init_file = Path(package) / "__init__.py"
        init_file.touch()
        print(f"Created __init__.py in: {package}")

def migrate_existing_files():
    """Migrate existing files to new structure"""
    
    migrations = [
        # (source, destination)
        ("MyProject/create_project_workbook.py", "src/core/excel_generator.py"),
        ("Hassan Rahman_2025-8-16-20-24-4_1.csv", "data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv"),
        ("MyProject/Project_Management.xlsx", "output/reports/financial/Project_Management.xlsx"),
        ("test.txt", "data/raw/test.txt")  # Move test file to raw data for now
    ]
    
    for source, destination in migrations:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            # Create destination directory if it doesn't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            print(f"Moved: {source} → {destination}")
        else:
            print(f"Source file not found: {source}")

def create_config_files():
    """Create configuration files"""
    
    # paths.json
    paths_config = """{
    "data_root": "data/",
    "output_root": "output/",
    "template_root": "templates/",
    "src_root": "src/",
    "sharepoint_data": "data/raw/sharepoint/",
    "financial_data": "data/raw/financial/",
    "academic_data": "data/raw/academic/",
    "processed_data": "data/processed/",
    "reports_output": "output/reports/",
    "dashboards_output": "output/dashboards/"
}"""
    
    with open("config/paths.json", "w") as f:
        f.write(paths_config)
    
    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Data files (exclude sensitive data)
data/raw/sharepoint/*.csv
data/external/
*.xlsx
*.xls

# Output files (generated content)
output/automated/
output/dashboards/*.png
output/reports/*.pdf

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("Created configuration files")

def create_readme():
    """Create README for the new structure"""
    
    readme_content = """# Rahman Analytics Hub

A comprehensive data analysis and business intelligence platform for Rahman Finance and Accounting P.L.LLC and WGU MBA coursework.

## Directory Structure

- `src/` - Source code modules
- `data/` - Data files (raw, processed, external)
- `output/` - Generated reports and analysis
- `templates/` - Reusable templates
- `config/` - Configuration files
- `docs/` - Documentation
- `tests/` - Unit tests
- `scripts/` - Utility scripts

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure paths in `config/paths.json`
3. Run analysis: `python scripts/run_analysis.py`

## Documentation

See `docs/` directory for detailed documentation.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("Created README.md")

def main():
    """Main setup function"""
    print("Setting up Rahman Analytics Hub directory structure...")
    
    # Create directory structure
    create_directory_structure()
    
    # Migrate existing files
    print("\nMigrating existing files...")
    migrate_existing_files()
    
    # Create config files
    print("\nCreating configuration files...")
    create_config_files()
    
    # Create README
    create_readme()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Review the new directory structure")
    print("2. Update file paths in your code")
    print("3. Create a virtual environment: python -m venv .venv")
    print("4. Install dependencies: pip install openpyxl pandas numpy matplotlib seaborn")
    print("5. Start developing with the new modular structure")

if __name__ == "__main__":
    main()