# 🎬 Live Demo: qwe + Easy-Ai Integration

## See It In Action! (Step-by-Step)

---

## **Prerequisites** ✅

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Flask installed: `pip install flask requests`
- ✅ Visual Studio with qwe project
- ✅ Both repositories cloned

---

## **Part 1: Start Demo MCP Server** (2 minutes)

### **Step 1: Open PowerShell**
```powershell
# Navigate to Easy-Ai repository
cd "E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai"
```

### **Step 2: Start Demo Server**
```powershell
python scripts/demo_mcp_server.py
```

**Expected Output:**
```
============================================================
🚀 Easy-Ai MCP Demo Server
============================================================

📍 Server URL: http://localhost:8080
🔧 Health Check: http://localhost:8080/health
📊 Dashboard: http://localhost:8080/api/security/dashboard
🚨 Alerts: http://localhost:8080/api/security/alerts

This is a DEMO server with sample data.
Use for testing qwe integration without M365 access.

Press Ctrl+C to stop
============================================================

 * Running on http://localhost:8080
 * Debug mode: on
```

### **Step 3: Keep This Window Open**
✅ Server is now running and waiting for requests

---

## **Part 2: Test the API** (2 minutes)

### **Open a NEW PowerShell Window**

```powershell
cd "E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai"

# Run integration test
python scripts/test_qwe_integration.py
```

**Expected Output:**
```
============================================================
🔗 qwe + Easy-Ai Integration Demo
============================================================

This simulates the API calls that the qwe website makes
to the Easy-Ai MCP server.

============================================================
Testing: Health Check
URL: http://localhost:8080/health
============================================================
✅ Status: 200 OK

📄 Response Data:
{
  "status": "healthy",
  "service": "Easy-Ai MCP Server (Demo)",
  "version": "1.0.0-demo",
  "timestamp": "2025-12-11T..."
}

============================================================
Testing: Security Dashboard
URL: http://localhost:8080/api/security/dashboard
============================================================
✅ Status: 200 OK

📄 Response Data:
{
  "status": "operational",
  "totalAlerts": 4,
  "criticalAlerts": 1,
  "highAlerts": 1,
  "mediumAlerts": 1,
  "lowAlerts": 1,
  "complianceScore": 82.45,
  "lastUpdated": "2025-12-11T...",
  "recentActivities": [
    "Security audit completed at 2025-12-11 08:00:00",
    "3 new alerts detected",
    "Compliance score improved by 2%"
  ]
}

[... more test results ...]

============================================================
📊 Test Summary
============================================================
✅ PASS - Health Check
✅ PASS - Security Dashboard
✅ PASS - Active Alerts
✅ PASS - Compliance Status
✅ PASS - SharePoint Analysis

Results: 5/5 tests passed

🎉 All tests passed! Integration is working!

Next steps:
1. Build qwe project in Visual Studio
2. Run qwe website
3. Navigate to: /Admin/Security/Dashboard
```

---

## **Part 3: Test in Browser** (1 minute)

### **Open Your Web Browser**

Visit these URLs to see the JSON responses:

1. **Health Check:**
   ```
   http://localhost:8080/health
   ```
   
   **You'll see:**
   ```json
   {
     "status": "healthy",
     "service": "Easy-Ai MCP Server (Demo)"
   }
   ```

2. **Security Dashboard:**
   ```
   http://localhost:8080/api/security/dashboard
   ```
   
   **You'll see:**
   ```json
   {
     "status": "operational",
     "totalAlerts": 4,
     "criticalAlerts": 1,
     "highAlerts": 1,
     "complianceScore": 82.45,
     "recentActivities": [...]
   }
   ```

3. **Active Alerts:**
   ```
   http://localhost:8080/api/security/alerts
   ```

---

## **Part 4: Integrate with qwe** (5 minutes)

### **Step 1: Setup qwe Integration**

```powershell
cd "E:\source\Heyson315\DjangoWebProject1\Heyson315\Easy-Ai"

# Run automated setup
.\scripts\setup_qwe_integration.ps1
```

**Expected Output:**
```
🔗 Easy-Ai + qwe Integration Setup
============================================================

📍 Verifying paths...
   ✅ Paths verified

📁 Copying integration files...
   ✅ Service class copied
   ✅ Controller copied
   ✅ View copied

⚙️  Configuration...
   ℹ️  Please add these settings to your Web.config manually:

   <add key="EasyAi:McpServerUrl" value="http://localhost:8080" />
   <add key="EasyAi:Enabled" value="true" />

📦 NuGet Packages...
   ✅ Newtonsoft.Json installed
   ✅ WebApi.Client installed

============================================================
✅ Integration setup complete!

Next Steps:
1. Build qwe project in Visual Studio
2. Start MCP server: python scripts/demo_mcp_server.py
3. Run qwe website
4. Navigate to: http://localhost:PORT/Admin/Security/Dashboard
============================================================
```

### **Step 2: Open qwe in Visual Studio**

1. Open Visual Studio
2. File → Open → Solution
3. Navigate to: `E:\source\Heyson315\qwe\qwe.sln`
4. Click **Open**

### **Step 3: Add Configuration**

Open `qwe/Web.config` and add:

```xml
<appSettings>
  <!-- Easy-Ai Integration -->
  <add key="EasyAi:McpServerUrl" value="http://localhost:8080" />
  <add key="EasyAi:Enabled" value="true" />
</appSettings>
```

### **Step 4: Build qwe**

In Visual Studio:
1. Build → Rebuild Solution
2. Wait for build to complete
3. Check Output window for any errors

### **Step 5: Run qwe**

1. Press **F5** or click **▶ Start**
2. Browser opens automatically
3. Login as administrator

### **Step 6: Navigate to Security Dashboard**

In the qwe admin portal:
1. Click **Admin** menu
2. Click **Security Dashboard**
3. **BOOM!** 🎉

---

## **Part 5: What You'll See** 🎨

### **Security Dashboard View:**

```
╔═══════════════════════════════════════════════════════════╗
║  🛡️  Security Dashboard              [Run Audit Now]     ║
╠═══════════════════════════════════════════════════════════╣
║  Real-time security monitoring powered by Easy-Ai         ║
║  Last updated: Just now                                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      ║
║  │ Total       │  │ Critical    │  │ High        │      ║
║  │ Alerts      │  │    🔴 1     │  │   🟠 1      │      ║
║  │    4        │  │             │  │             │      ║
║  └─────────────┘  └─────────────┘  └─────────────┘      ║
║                                                            ║
║  ┌─────────────┐  ┌─────────────────────────────────┐   ║
║  │ Compliance  │  │ [Doughnut Chart]                │   ║
║  │ Score       │  │  Critical: 25%                  │   ║
║  │   82.5%     │  │  High: 25%                      │   ║
║  │     🟢      │  │  Medium: 25%                    │   ║
║  └─────────────┘  │  Low: 25%                       │   ║
║                   └─────────────────────────────────┘   ║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐║
║  │ Recent Security Alerts                              │║
║  ├──────────┬─────────┬───────────────┬─────────┬─────┤║
║  │ Severity │ Source  │ Title         │ Status  │ Date│║
║  ├──────────┼─────────┼───────────────┼─────────┼─────┤║
║  │🔴CRITICAL│M365 CIS │MFA Not Enforc│ Open    │12/10│║
║  │🟠HIGH    │Safety   │Outdated Pkg  │ Open    │12/11│║
║  │🟡MEDIUM  │SharePoi │External Share│ Open    │12/11│║
║  │🟢LOW     │Bandit   │Weak Hash     │ Ack     │12/09│║
║  └──────────┴─────────┴───────────────┴─────────┴─────┘║
║                                                            ║
║  ┌──────────────────────────────────────────────────────┐║
║  │ Recent Activities                                    │║
║  │  • Security audit completed at 2025-12-11 08:00:00  │║
║  │  • 3 new alerts detected                            │║
║  │  • Compliance score improved by 2%                  │║
║  │  • SharePoint permissions analyzed for 12 sites     │║
║  │  • Critical alert M365-001 requires attention       │║
║  └──────────────────────────────────────────────────────┘║
╚═══════════════════════════════════════════════════════════╝
```

---

## **Part 6: Interactive Demo Actions**

### **Action 1: Click "Run Audit Now"**

1. Click the blue **"Run Audit Now"** button
2. Alert popup: "Start a new security audit? This may take several minutes."
3. Click **OK**
4. Success message: "Security audit started successfully!"
5. Page reloads with updated data

### **Action 2: View Detailed Alerts**

1. Click **"View All Alerts"** link
2. New page opens with full alerts list
3. Filter by severity: Critical, High, Medium, Low
4. Click individual alert for details

### **Action 3: Check Compliance**

1. Click **"Compliance"** in navigation
2. View detailed CIS controls breakdown
3. See pass/fail status for each control
4. Review trend analysis

### **Action 4: SharePoint Analysis**

1. Click **"SharePoint"** in navigation
2. View permissions analysis
3. See risky permissions list
4. Review site-level security

---

## **Part 7: Behind the Scenes** 🔍

While you're viewing the dashboard, this is happening:

### **Step 1: Browser Request**
```
Browser → GET /Admin/Security/Dashboard → qwe Server
```

### **Step 2: Controller Action**
```csharp
// AdminSecurityController.cs
public async Task<ActionResult> Dashboard()
{
    var dashboard = await _securityService.GetSecurityDashboardAsync();
    // HTTP GET http://localhost:8080/api/security/dashboard
    
    ViewBag.Dashboard = dashboard;
    return View();
}
```

### **Step 3: MCP Server Response**
```python
# demo_mcp_server.py
@app.route('/api/security/dashboard')
def get_dashboard():
    return jsonify({
        "totalAlerts": 4,
        "criticalAlerts": 1,
        "complianceScore": 82.45,
        # ...
    })
```

### **Step 4: View Rendering**
```razor
<!-- Dashboard.cshtml -->
<h2>Total Alerts: @dashboard.TotalAlerts</h2>
<h2>Compliance: @dashboard.ComplianceScore%</h2>
<!-- Charts rendered with Chart.js -->
```

---

## **Part 8: Stop the Demo**

When you're done:

1. **Stop MCP Server:**
   - Go to PowerShell window with demo server
   - Press **Ctrl+C**
   
2. **Stop qwe:**
   - In Visual Studio, click **⏹ Stop**

---

## **Troubleshooting**

### **Issue: "MCP server not running"**

**Solution:**
```powershell
# Check if server is running
netstat -ano | findstr ":8080"

# If nothing appears, start server
python scripts/demo_mcp_server.py
```

### **Issue: "Connection refused"**

**Solution:**
```powershell
# Check Windows Firewall
# Allow Python through firewall:
netsh advfirewall firewall add rule name="Python" dir=in action=allow program="C:\Path\To\python.exe"
```

### **Issue: "Dashboard shows error"**

**Solution:**
1. Check MCP server is running
2. Verify Web.config has correct URL
3. Check browser console for errors
4. Verify qwe can reach localhost:8080

---

## **Next Steps**

Once demo is working:

1. **Replace with real MCP server:**
   ```powershell
   python -m src.mcp.m365_mcp_server
   ```

2. **Run actual M365 audit:**
   ```powershell
   powershell scripts/powershell/Invoke-M365CISAudit.ps1
   ```

3. **See real security data** in dashboard!

---

## **Video Demo** 🎥

Want to record a video?

1. Start demo server
2. Open qwe in browser
3. Use Windows Game Bar: **Win+G**
4. Click record button
5. Navigate through dashboard
6. Show all features

---

**Ready to see it live?** 🚀

Run these commands in order:
```powershell
# Terminal 1: Start demo server
python scripts/demo_mcp_server.py

# Terminal 2: Test API
python scripts/test_qwe_integration.py

# Terminal 3: Open in browser
Start-Process "http://localhost:8080/api/security/dashboard"
```

Then build and run qwe in Visual Studio!

---

**Demo Files Created:**
- ✅ `scripts/demo_mcp_server.py` - Demo API server
- ✅ `scripts/test_qwe_integration.py` - API test client
- ✅ `LIVE_DEMO_GUIDE.md` - This guide

**Time to Live Demo:** ~10 minutes  
**Coolness Factor:** 💯/100
