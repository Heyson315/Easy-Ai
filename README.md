# Rahman Analytics Hub

A comprehensive data analysis and business intelligence platform for Rahman Finance and Accounting P.L.LLC and WGU MBA coursework.

## 📁 Project Structure

```
Rahman_Analytics_Hub/
├── .github/
│   └── copilot-instructions.md    # AI agent guidelines
├── src/                           # Source code modules
│   ├── core/                      # Core functionality
│   │   └── excel_generator.py     # Main Excel workbook generator
│   ├── financial/                 # Financial analysis
│   ├── analytics/                 # Data science (C207)
│   ├── business/                  # Business intelligence  
│   ├── academic/                  # WGU MBA coursework
│   └── integrations/              # External systems
├── data/                          # Data files
│   ├── raw/                       # Unprocessed data
│   │   ├── sharepoint/            # SharePoint permissions data
│   │   ├── financial/             # Financial transaction data
│   │   └── academic/              # Course datasets
│   ├── processed/                 # Cleaned data
│   ├── external/                  # External API data
│   └── archive/                   # Historical backups
├── output/                        # Generated reports
│   ├── reports/                   # Analysis reports
│   │   ├── financial/             # Financial workbooks
│   │   ├── academic/              # Academic analysis
│   │   └── business/              # Business intelligence
│   ├── dashboards/                # Interactive dashboards
│   ├── presentations/             # Presentation materials
│   └── automated/                 # Scheduled outputs
├── templates/                     # Reusable templates
│   ├── excel/                     # Excel templates
│   ├── python/                    # Code templates
│   └── academic/                  # Academic project templates
├── config/                        # Configuration files
├── docs/                          # Documentation
├── tests/                         # Unit tests
└── scripts/                       # Utility scripts
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Basic Usage
```python
# Generate a financial workbook
from src.core.excel_generator import create_workbook
wb = create_workbook()
wb.save('output/reports/financial/my_report.xlsx')
```

### 3. Process SharePoint Data
```python
# Analyze SharePoint permissions
from src.integrations.sharepoint_connector import process_permissions
data = process_permissions('data/raw/sharepoint/Hassan Rahman_2025-8-16-20-24-4_1.csv')
```

### 4. C207 Data Science Workflow
```python
# Run C207 analytics pipeline
from src.analytics.c207_workflows import run_analysis
results = run_analysis('dataset.csv', analysis_type='descriptive')
```

## 📊 Key Features

### Financial Management
- ✅ Automated Excel workbook generation
- ✅ Transaction tracking and budget analysis
- ✅ Financial reporting templates

### Data Science (C207)
- ✅ Descriptive and inferential statistics
- ✅ Data visualization and charting
- ✅ Statistical hypothesis testing
- ✅ Business analytics workflows

### Business Intelligence
- ✅ SWOT analysis automation
- ✅ Strategic analysis frameworks
- ✅ Project management reporting
- ✅ SharePoint permissions analysis

### Academic Integration
- ✅ WGU MBA coursework support
- ✅ Standardized analysis templates
- ✅ Research and investigation tools

## 🔧 Configuration

Edit `config/paths.json` to customize file locations:
```json
{
    "data_root": "data/",
    "output_root": "output/",
    "sharepoint_data": "data/raw/sharepoint/"
}
```

## 📚 Documentation

- **AI Guidelines**: See `.github/copilot-instructions.md` for detailed patterns
- **File Organization**: See `FILE_ORGANIZATION_GUIDE.md`
- **Next Steps**: See `NEXT_STEPS.md` for development roadmap

## 🎯 Use Cases

### For Rahman Finance and Accounting P.L.LLC
- Automated client reporting
- Financial data analysis
- Business intelligence dashboards

### For WGU MBA Coursework
- C207 data science projects
- Strategic analysis (SWOT, competitive analysis)
- Project management analysis
- Academic research and reporting

## 🤝 Contributing

This project uses AI-assisted development. See `.github/copilot-instructions.md` for guidelines on working with AI coding agents.

## 📄 License

Copyright (c) 2025 Rahman Finance and Accounting P.L.LLC