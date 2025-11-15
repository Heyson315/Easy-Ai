#!/usr/bin/env python3
"""
generate_security_dashboard.py

Generate an interactive HTML dashboard from M365 CIS audit JSON results.
Features:
- Summary cards (Pass/Fail/Manual counts, severity breakdown)
- Trend charts if historical data exists
- Control status table with filtering/sorting
- Failed controls highlighted with remediation links
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def load_audit_results(json_path: Path) -> List[Dict[str, Any]]:
    """Load audit results from JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except (PermissionError, FileNotFoundError) as e:
        print(f"ERROR: Cannot read {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: I/O error reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"ERROR: Encoding error reading {json_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Validate data is a list
    if not isinstance(data, list):
        print(f"ERROR: Expected JSON array, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)
    
    if not data:
        print(f"WARNING: No audit results found in {json_path}", file=sys.stderr)
    
    return data


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics from audit results."""
    stats = {
        "total": len(results),
        "pass": 0,
        "fail": 0,
        "manual": 0,
        "error": 0,
        "by_severity": {"High": 0, "Medium": 0, "Low": 0},
        "failed_by_severity": {"High": 0, "Medium": 0, "Low": 0},
    }

    for result in results:
        status = result.get("Status", "Unknown")
        severity = result.get("Severity", "Unknown")

        if status == "Pass":
            stats["pass"] += 1
        elif status == "Fail":
            stats["fail"] += 1
            if severity in stats["failed_by_severity"]:
                stats["failed_by_severity"][severity] += 1
        elif status == "Manual":
            stats["manual"] += 1
        elif status == "Error":
            stats["error"] += 1

        if severity in stats["by_severity"]:
            stats["by_severity"][severity] += 1

    stats["pass_rate"] = round((stats["pass"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0
    stats["fail_rate"] = round((stats["fail"] / stats["total"]) * 100, 2) if stats["total"] > 0 else 0

    return stats


def load_historical_data(reports_dir: Path) -> List[Dict[str, Any]]:
    """Load historical audit data for trend analysis."""
    historical = []

    # Look for timestamped JSON files
    json_files = sorted(reports_dir.glob("m365_cis_audit_*.json"))

    for json_file in json_files:
        try:
            results = load_audit_results(json_file)
            stats = calculate_statistics(results)

            # Extract timestamp from filename (format: m365_cis_audit_YYYYMMDD_HHMMSS.json)
            filename = json_file.stem
            if "_" in filename:
                parts = filename.split("_")
                if len(parts) >= 5:
                    date_str = parts[3]
                    time_str = parts[4] if len(parts) > 4 else "000000"
                    try:
                        timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                        historical.append(
                            {
                                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
                                "pass_rate": stats["pass_rate"],
                                "pass": stats["pass"],
                                "fail": stats["fail"],
                                "manual": stats["manual"],
                            }
                        )
                    except ValueError as e:
                        print(f"Warning: Could not parse timestamp from {json_file.name}: {e}", file=sys.stderr)
                        continue
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {json_file.name}: {e}", file=sys.stderr)
            continue
        except FileNotFoundError:
            print(f"Warning: File disappeared during processing: {json_file.name}", file=sys.stderr)
            continue
        except (KeyError, TypeError) as e:
            print(f"Warning: Unexpected data structure in {json_file.name}: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Warning: Unexpected error processing {json_file.name}: {type(e).__name__}: {e}", file=sys.stderr)
            continue

    return historical[-10:]  # Return last 10 data points


def generate_html_dashboard(
    results: List[Dict[str, Any]], stats: Dict[str, Any], historical: List[Dict[str, Any]], output_path: Path
):
    """Generate interactive HTML dashboard."""

    # Prepare data for charts
    trend_labels = [h["timestamp"] for h in historical]
    trend_pass_rates = [h["pass_rate"] for h in historical]

    # Sort results by severity and status
    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    status_order = {"Fail": 0, "Error": 1, "Manual": 2, "Pass": 3}

    sorted_results = sorted(
        results,
        key=lambda x: (severity_order.get(x.get("Severity", "Low"), 3), status_order.get(x.get("Status", "Pass"), 3)),
    )

    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M365 CIS Security Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #0078d4;
            margin-bottom: 10px;
        }}
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }}
        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-value.pass {{ color: #28a745; }}
        .stat-value.fail {{ color: #dc3545; }}
        .stat-value.manual {{ color: #6c757d; }}
        .stat-card .subtitle {{
            color: #999;
            font-size: 12px;
        }}
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: {'block' if len(historical) > 1 else 'none'};
        }}
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }}
        .controls-table {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .controls-table h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }}
        .filter-controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        .filter-btn:hover {{
            background: #f8f9fa;
        }}
        .filter-btn.active {{
            background: #0078d4;
            color: white;
            border-color: #0078d4;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #0078d4;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-pass {{ background: #d4edda; color: #155724; }}
        .status-fail {{ background: #f8d7da; color: #721c24; }}
        .status-manual {{ background: #e2e3e5; color: #383d41; }}
        .status-error {{ background: #fff3cd; color: #856404; }}
        .severity-high {{ color: #dc3545; font-weight: bold; }}
        .severity-medium {{ color: #fd7e14; font-weight: bold; }}
        .severity-low {{ color: #6c757d; }}
        .control-title {{
            font-weight: 500;
            color: #333;
        }}
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ M365 CIS Security Dashboard</h1>
            <div class="meta">
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                <strong>Total Controls:</strong> {stats['total']} |
                <strong>Pass Rate:</strong> {stats['pass_rate']}%
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Passed Controls</h3>
                <div class="stat-value pass">{stats['pass']}</div>
                <div class="subtitle">{stats['pass_rate']}% of total</div>
            </div>
            <div class="stat-card">
                <h3>Failed Controls</h3>
                <div class="stat-value fail">{stats['fail']}</div>
                <div class="subtitle">{stats['fail_rate']}% of total</div>
            </div>
            <div class="stat-card">
                <h3>Manual Review</h3>
                <div class="stat-value manual">{stats['manual']}</div>
                <div class="subtitle">Requires investigation</div>
            </div>
            <div class="stat-card">
                <h3>High Severity Failures</h3>
                <div class="stat-value fail">{stats['failed_by_severity']['High']}</div>
                <div class="subtitle">Critical issues</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📈 Pass Rate Trend</h2>
            <canvas id="trendChart"></canvas>
        </div>

        <div class="controls-table">
            <h2>🔍 Control Status Details</h2>
            <div class="filter-controls">
                <button class="filter-btn active" onclick="filterTable('all')">All</button>
                <button class="filter-btn" onclick="filterTable('pass')">Pass</button>
                <button class="filter-btn" onclick="filterTable('fail')">Fail</button>
                <button class="filter-btn" onclick="filterTable('manual')">Manual</button>
                <button class="filter-btn" onclick="filterTable('high')">High Severity</button>
            </div>
            <table id="controlsTable">
                <thead>
                    <tr>
                        <th>Control ID</th>
                        <th>Title</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Actual</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add table rows
    for result in sorted_results:
        control_id = result.get("ControlId", "N/A")
        title = result.get("Title", "N/A")
        severity = result.get("Severity", "Unknown")
        status = result.get("Status", "Unknown")
        actual = result.get("Actual", "N/A")

        status_class = f"status-{status.lower()}"
        severity_class = f"severity-{severity.lower()}"

        html_content += f"""
                    <tr data-status="{status.lower()}" data-severity="{severity.lower()}">
                        <td><strong>{control_id}</strong></td>
                        <td class="control-title">{title}</td>
                        <td class="{severity_class}">{severity}</td>
                        <td><span class="status-badge {status_class}">{status}</span></td>
                        <td>{actual}</td>
                    </tr>
"""

    html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>Next Audit Recommended:</strong> {(datetime.now()).strftime('%Y-%m-%d')}
            (7 days from last audit)</p>
            <p>For remediation guidance, see PostRemediateM365CIS.ps1 with -WhatIf parameter</p>
        </div>
    </div>

    <script>
        // Trend Chart
        const ctx = document.getElementById('trendChart');
        if (ctx) {{
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {json.dumps(trend_labels)},
                    datasets: [{{
                        label: 'Pass Rate (%)',
                        data: {json.dumps(trend_pass_rates)},
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        // Filter functionality
        function filterTable(filter) {{
            const rows = document.querySelectorAll('#controlsTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');

            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            // Filter rows
            rows.forEach(row => {{
                const status = row.dataset.status;
                const severity = row.dataset.severity;

                if (filter === 'all') {{
                    row.style.display = '';
                }} else if (filter === 'high') {{
                    row.style.display = severity === 'high' ? '' : 'none';
                }} else {{
                    row.style.display = status === filter ? '' : 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    # Write HTML to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description="Generate M365 CIS Security Dashboard")
    parser.add_argument(
        "--input", type=Path, help="Path to audit JSON file (default: latest in output/reports/security/)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/reports/security/dashboard.html"),
        help="Output HTML file path (default: output/reports/security/dashboard.html)",
    )

    args = parser.parse_args()

    # Find input file
    if args.input:
        input_path = args.input
    else:
        # Look for latest audit file
        reports_dir = Path("output/reports/security")
        json_files = list(reports_dir.glob("m365_cis_audit*.json"))
        if not json_files:
            print("ERROR: No audit JSON files found in output/reports/security/", file=sys.stderr)
            print("Run Invoke-M365CISAudit.ps1 first to generate audit data.", file=sys.stderr)
            sys.exit(1)
        input_path = max(json_files, key=lambda p: p.stat().st_mtime)
        print(f"Using latest audit file: {input_path}")

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load and process data
    print(f"Loading audit results from {input_path}...")
    results = load_audit_results(input_path)
    stats = calculate_statistics(results)

    print(f"Calculating statistics: {stats['total']} controls, {stats['pass_rate']}% pass rate")

    # Load historical data
    reports_dir = input_path.parent
    historical = load_historical_data(reports_dir)
    if historical:
        print(f"Found {len(historical)} historical data points for trend analysis")

    # Generate dashboard
    print(f"Generating HTML dashboard: {args.output}")
    generate_html_dashboard(results, stats, historical, args.output)

    print(f"✅ Dashboard generated successfully: {args.output}")
    print(f"   Open in browser to view: file://{args.output.absolute()}")


if __name__ == "__main__":
    main()
