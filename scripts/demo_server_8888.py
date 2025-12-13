#!/usr/bin/env python3
"""
All-in-One Demo Server - Port 8888

Uses port 8888 to avoid conflicts with Docker or other services on 8080.

Usage:
    python scripts/demo_server_8888.py
    
Then open: http://localhost:8888
"""

from flask import Flask, jsonify, send_file
from datetime import datetime
import random
import os
from pathlib import Path

app = Flask(__name__)

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Sample data
SAMPLE_ALERTS = [
    {
        "id": "M365-001",
        "source": "m365_cis",
        "severity": "CRITICAL",
        "title": "Multi-Factor Authentication Not Enforced",
        "description": "MFA is not required for all users",
        "status": "open",
        "createdAt": "2025-12-10T14:30:00Z"
    },
    {
        "id": "SAF-002",
        "source": "safety",
        "severity": "HIGH",
        "title": "Outdated Package: requests 2.25.0",
        "description": "Security vulnerability in requests library",
        "status": "open",
        "createdAt": "2025-12-11T09:15:00Z"
    },
    {
        "id": "SPO-003",
        "source": "sharepoint",
        "severity": "MEDIUM",
        "title": "External Sharing Enabled",
        "description": "SharePoint site allows external sharing",
        "status": "open",
        "createdAt": "2025-12-11T11:00:00Z"
    },
    {
        "id": "BAN-004",
        "source": "bandit",
        "severity": "LOW",
        "title": "Weak Cryptographic Hash",
        "description": "MD5 hash detected in code",
        "status": "acknowledged",
        "createdAt": "2025-12-09T16:45:00Z"
    }
]

RECENT_ACTIVITIES = [
    "Security audit completed at 2025-12-11 08:00:00",
    "3 new alerts detected",
    "Compliance score improved by 2%",
    "SharePoint permissions analyzed for 12 sites",
    "Critical alert M365-001 requires immediate attention"
]


# === Serve the HTML Dashboard ===

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    # HTML file is in project root, not in scripts/
    html_path = PROJECT_ROOT / 'demo_dashboard_8888.html'
    return send_file(html_path)


# === API Endpoints ===

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Easy-Ai MCP Server (Demo - Port 8888)",
        "version": "1.0.0-demo",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/status')
def api_status():
    """Alternative status endpoint"""
    return jsonify({
        "status": "operational",
        "uptime": "24h 15m",
        "lastAudit": "2025-12-11T08:00:00Z"
    })


@app.route('/api/security/dashboard')
def get_dashboard():
    """Get security dashboard data"""
    critical = sum(1 for a in SAMPLE_ALERTS if a['severity'] == 'CRITICAL')
    high = sum(1 for a in SAMPLE_ALERTS if a['severity'] == 'HIGH')
    medium = sum(1 for a in SAMPLE_ALERTS if a['severity'] == 'MEDIUM')
    low = sum(1 for a in SAMPLE_ALERTS if a['severity'] == 'LOW')
    
    return jsonify({
        "status": "operational",
        "totalAlerts": len(SAMPLE_ALERTS),
        "criticalAlerts": critical,
        "highAlerts": high,
        "mediumAlerts": medium,
        "lowAlerts": low,
        "complianceScore": round(random.uniform(75, 95), 2),
        "lastUpdated": datetime.utcnow().isoformat(),
        "recentActivities": RECENT_ACTIVITIES
    })


@app.route('/api/security/alerts')
def get_alerts():
    """Get active security alerts"""
    return jsonify({
        "totalCount": len(SAMPLE_ALERTS),
        "alerts": SAMPLE_ALERTS
    })


@app.route('/api/security/compliance')
def get_compliance():
    """Get M365 CIS compliance status"""
    total = 50
    passed = 38
    failed = 8
    manual = 4
    
    return jsonify({
        "score": round((passed / total) * 100, 2),
        "totalControls": total,
        "passedControls": passed,
        "failedControls": failed,
        "manualControls": manual,
        "trend": "improving",
        "lastAudit": datetime.utcnow().isoformat()
    })


@app.route('/api/security/sharepoint')
def get_sharepoint():
    """Get SharePoint permissions analysis"""
    return jsonify({
        "totalSites": 12,
        "totalUsers": 145,
        "permissionIssues": 7,
        "riskyPermissions": [
            "External sharing enabled on Finance site",
            "Guest users with Full Control on Projects site",
            "Anonymous links created for HR site"
        ],
        "lastAnalyzed": datetime.utcnow().isoformat()
    })


@app.route('/api/security/audit', methods=['POST'])
def trigger_audit():
    """Trigger a new security audit"""
    import uuid
    job_id = str(uuid.uuid4())
    
    return jsonify({
        "jobId": job_id,
        "status": "started",
        "message": "Security audit initiated successfully",
        "startedAt": datetime.utcnow().isoformat(),
        "estimatedCompletion": "10 minutes"
    }), 202


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Easy-Ai Demo Server (Port 8888)")
    print("=" * 60)
    print()
    print("📍 Dashboard: http://localhost:8888")
    print("🔧 Health Check: http://localhost:8888/health")
    print("📊 API: http://localhost:8888/api/security/*")
    print()
    print("✅ Using port 8888 to avoid Docker conflicts!")
    print("✅ Just open http://localhost:8888 in your browser")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host='localhost', port=8888, debug=True)
