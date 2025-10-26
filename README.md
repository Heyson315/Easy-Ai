# M365 Security & SharePoint Analysis Toolkit 🛡️

[![CI/CD Pipeline](https://github.com/Heyson315/share-report/actions/workflows/m365-security-ci.yml/badge.svg)](https://github.com/Heyson315/share-report/actions/workflows/m365-security-ci.yml)
[![Monthly Security Audit](https://github.com/Heyson315/share-report/actions/workflows/m365-automated-audit.yml/badge.svg)](https://github.com/Heyson315/share-report/actions/workflows/m365-automated-audit.yml)
[![PowerShell](https://img.shields.io/badge/PowerShell-5.1+-blue.svg)](https://docs.microsoft.com/en-us/powershell/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/downloads/)

## 🎯 Overview

Enterprise-ready Microsoft 365 security auditing and SharePoint permissions analysis toolkit with comprehensive automation, performance monitoring, and compliance reporting capabilities.

### ✨ Key Features

- 🔐 **CIS Controls Compliance**: Automated M365 CIS benchmark assessments
- 📊 **SharePoint Analysis**: Detailed permissions and access reporting  
- 🤖 **GitHub Actions CI/CD**: Automated quality checks and monthly audits
- 📈 **Performance Monitoring**: Built-in benchmarking and validation
- 📱 **Interactive Dashboards**: HTML security scorecards with trend analysis
- 🔧 **Service Principal Ready**: Unattended automation support
- 🐍 **Hybrid Architecture**: PowerShell + Python for optimal performance

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** or **Windows Server 2019+**
- **PowerShell 5.1+** 
- **Python 3.9+**
- **M365 tenant** with admin access

### Installation

```bash
# Clone the repository
git clone https://github.com/Heyson315/share-report.git
cd share-report

# Setup Python environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Install PowerShell modules
Install-Module Microsoft.Graph.Authentication, ExchangeOnlineManagement -Scope CurrentUser
```

### Basic Usage

```powershell
# Import the M365 CIS module
Import-Module "scripts/powershell/modules/M365CIS.psm1"

# Connect to M365 services
Connect-M365CIS

# Run comprehensive security audit
$results = Invoke-M365CISAudit -Timestamped

# Generate reports
$results | ConvertTo-Json | Out-File "output/reports/security/audit-results.json"
python scripts/m365_cis_report.py  # Creates Excel report
python scripts/generate_security_dashboard.py  # Creates HTML dashboard
```

## 📁 Project Structure

```
📦 M365 Security Toolkit
├── 📂 .github/workflows/          # GitHub Actions CI/CD
│   ├── m365-security-ci.yml       # Quality checks & testing
│   └── m365-automated-audit.yml   # Monthly security audits
├── 📂 config/                     # Configuration files
│   ├── audit_config.json          # Main audit configuration
│   └── benchmarks/                # CIS control definitions
├── 📂 data/                       # Data processing directories
│   ├── raw/                       # Unprocessed exports
│   ├── processed/                 # Cleaned CSV files
│   └── archive/                   # Historical snapshots
├── 📂 docs/                       # Documentation
│   ├── M365_SERVICE_PRINCIPAL_SETUP.md   # Automation setup guide
│   ├── PRODUCTION_DEPLOYMENT.md          # Enterprise deployment
│   ├── SECURITY_M365_CIS.md              # Security audit workflow
│   └── USAGE_SHAREPOINT.md               # SharePoint analysis guide
├── 📂 output/reports/             # Generated reports
│   ├── security/                  # JSON/CSV audit results
│   └── business/                  # Excel/HTML reports
├── 📂 scripts/                    # Automation scripts
│   ├── 🐍 Python processing scripts
│   └── 📂 powershell/modules/     # M365CIS PowerShell module
├── 📂 src/                        # Core toolkit modules
│   ├── core/                      # Excel generation
│   └── integrations/              # SharePoint connector
└── 📂 tests/                      # Automated testing
```

## 🔧 Core Workflows

### 1. M365 CIS Security Audit

```powershell
# Complete automated audit
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/powershell/Invoke-M365CISAudit.ps1" -Timestamped

# Convert to Excel report
python scripts/m365_cis_report.py

# Generate interactive dashboard
python scripts/generate_security_dashboard.py
```

**Covers**: Exchange Online, Azure AD, SharePoint Online, Microsoft Defender, Intune compliance policies

### 2. SharePoint Permissions Analysis

```powershell
# Clean raw SharePoint export
python scripts/clean_csv.py --input "data/raw/sharepoint/permissions.csv" --output "data/processed/sharepoint_clean.csv"

# Generate business report
python -m src.integrations.sharepoint_connector --input "data/processed/sharepoint_clean.csv"
```

**Output**: Detailed Excel reports with user access summaries, permission inheritance analysis, and security recommendations

### 3. Performance Benchmarking

```python
# Run performance validation
python scripts/run_performance_benchmark.py --baseline

# Compare against benchmarks
python scripts/run_performance_benchmark.py --validate-against-baseline
```

**Validates**: JSON/CSV processing speeds, memory usage, Excel generation performance

## 🤖 Automation Features

### GitHub Actions CI/CD

- **Quality Assurance**: Python linting, PowerShell analysis, security scanning
- **Automated Testing**: Unit tests, integration tests, performance validation
- **Monthly Audits**: Scheduled M365 security assessments with artifact preservation
- **Dependency Updates**: Automated dependency scanning and updates

### Service Principal Authentication

Supports unattended automation with Azure AD service principals:

```powershell
# Setup automated authentication
Connect-M365CIS-ServicePrincipal -TenantId $tenantId -ClientId $clientId -ClientSecret $secret

# Runs without interactive prompts
$results = Invoke-M365CISAudit -Automated
```

See [`docs/M365_SERVICE_PRINCIPAL_SETUP.md`](docs/M365_SERVICE_PRINCIPAL_SETUP.md) for detailed configuration.

## 📊 Reporting Capabilities

### Security Dashboards
- **Interactive HTML reports** with Chart.js visualizations
- **Historical trend analysis** across multiple audit runs
- **Control status filtering** and drill-down capabilities
- **Compliance scoring** with CIS benchmark alignment

### Business Reports
- **Executive summaries** with risk scoring
- **Detailed technical findings** with remediation guidance
- **SharePoint access analysis** with user permission matrices
- **Performance metrics** and trend analysis

### Export Formats
- **JSON**: Raw audit data for API integration
- **CSV**: Tabular data for analysis tools
- **Excel**: Formatted business reports with charts
- **HTML**: Interactive dashboards for stakeholders

## 🛡️ Security Features

### Compliance Standards
- **CIS Microsoft 365 Foundations Benchmark** v3.0.0
- **NIST Cybersecurity Framework** mapping
- **ISO 27001** control alignment
- **Custom security policies** support

### Security Controls
- **Data encryption** for sensitive configuration files
- **Audit logging** for all script executions
- **Access control** with role-based permissions
- **Secure credential storage** using PowerShell SecureString

## 🚀 Production Deployment

### Quick Production Setup

1. **Clone and configure** the repository
2. **Setup service principal** authentication ([guide](docs/M365_SERVICE_PRINCIPAL_SETUP.md))
3. **Configure GitHub secrets** for automated auditing
4. **Customize audit parameters** in `config/audit_config.json`
5. **Deploy and monitor** via GitHub Actions

See [`docs/PRODUCTION_DEPLOYMENT.md`](docs/PRODUCTION_DEPLOYMENT.md) for comprehensive enterprise deployment instructions.

### Scalability
- **Multi-tenant support** for MSP environments
- **High-frequency auditing** (hourly/daily options)
- **Large dataset optimization** with chunked processing
- **Performance monitoring** with automated alerting

## 📈 Performance Benchmarks

| Operation | Small Dataset | Medium Dataset | Large Dataset |
|-----------|---------------|----------------|---------------|
| JSON Processing | <2s | <5s | <15s |
| CSV Cleaning | <1s | <3s | <8s |
| Excel Generation | <5s | <12s | <30s |
| Full CIS Audit | <60s | <180s | <300s |

*Benchmarks based on Windows 10 with 16GB RAM, SSD storage*

## 🔍 Troubleshooting

### Common Issues

**Authentication Failures**
```powershell
# Test connectivity
Test-MgGraph
Get-ConnectionInformation  # Exchange Online
```

**Performance Issues**
```python
# Monitor memory usage
python scripts/monitor_memory_usage.py --during-audit
```

**GitHub Actions Failures**
```bash
# View detailed logs
gh run view --log
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft** for comprehensive M365 APIs and PowerShell modules
- **CIS** for security benchmark standards
- **Community** contributors and security researchers
- **GitHub Actions** for enabling robust CI/CD automation

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Heyson315/share-report/issues)
- 📚 **Documentation**: [`docs/`](docs/) directory
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Heyson315/share-report/discussions)
- 📧 **Security Issues**: security@company.com

---

**⭐ If this toolkit helps secure your M365 environment, please give it a star!**