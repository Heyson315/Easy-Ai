import json
import sys

data = json.load(open('output/reports/security/m365_cis_audit_20251111_121220.json', 'r', encoding='utf-8-sig'))
statuses = [c['Status'] for c in data]
passed = statuses.count('Pass')
failed = statuses.count('Fail')
manual = statuses.count('Manual')
total = len(statuses)

print(f"Pass: {passed}, Fail: {failed}, Manual: {manual}, Total: {total}")
print(f"Compliance: {passed/total*100:.1f}%")

# Show which controls changed
print("\n=== Control Status ===")
for c in data:
    status_icon = "✅" if c['Status'] == 'Pass' else "❌" if c['Status'] == 'Fail' else "⚠️"
    print(f"{status_icon} {c['ControlId']}: {c['Title'][:60]} - {c['Status']}")
