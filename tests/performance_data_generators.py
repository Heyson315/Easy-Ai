"""
Performance Testing Data Generators
Generates synthetic test data for M365 Security Toolkit performance testing
"""

import json
import csv
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import tempfile


class M365CISDataGenerator:
    """Generate synthetic M365 CIS audit data for performance testing"""
    
    CONTROL_IDS = [
        "1.1.1", "1.1.2", "1.1.3", "1.2.1", "1.2.2", "1.3.1", "1.3.2", "1.3.3",
        "2.1.1", "2.1.2", "2.1.3", "2.1.4", "2.1.5", "2.1.6", "2.1.7", "2.1.8",
        "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.2.1", "3.2.2", "3.2.3", "3.2.4",
        "4.1.1", "4.1.2", "4.1.3", "4.2.1", "4.2.2", "4.2.3", "4.2.4", "4.2.5",
        "5.1.1", "5.1.2", "5.1.3", "5.1.4", "5.1.5", "5.2.1", "5.2.2", "5.2.3"
    ]
    
    SEVERITIES = ["Critical", "High", "Medium", "Low"]
    STATUSES = ["Pass", "Fail", "Manual", "NotApplicable"]
    
    SAMPLE_TITLES = [
        "Ensure modern authentication for Exchange Online is enabled",
        "Ensure that Office 365 ATP SafeLinks for Office Applications is Enabled",
        "Ensure Microsoft 365 audit log search is Enabled",
        "Ensure that an anti-phishing policy has been created",
        "Ensure Exchange Online spam policies are set correctly",
        "Ensure that DKIM is enabled for all Exchange Online Domains",
        "Ensure that SPF records are published for all Exchange Online domains",
        "Ensure calendar details sharing with external users is disabled",
        "Ensure MailTips are enabled for end users",
        "Ensure user consent to apps accessing company data on their behalf is not allowed"
    ]
    
    def generate_control_result(self, control_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate a single CIS control result"""
        title_base = random.choice(self.SAMPLE_TITLES)
        status = random.choice(self.STATUSES)
        severity = random.choice(self.SEVERITIES)
        
        # Generate realistic evidence based on status
        if status == "Pass":
            evidence = f"Configuration verified: {title_base.lower()} is properly configured"
        elif status == "Fail":
            evidence = f"Non-compliance detected: {title_base.lower()} requires attention"
        else:
            evidence = f"Manual review required for {title_base.lower()}"
        
        return {
            "ControlId": control_id,
            "Title": f"{title_base} (Control {control_id})",
            "Severity": severity,
            "Expected": "Compliant configuration as per CIS benchmark",
            "Actual": f"Current status: {status}",
            "Status": status,
            "Evidence": evidence,
            "Reference": f"CIS Microsoft 365 Foundations Benchmark v3.0.0 - {control_id}",
            "Timestamp": timestamp.isoformat(),
            "TenantId": self._generate_guid(),
            "AssessmentId": self._generate_guid()
        }
    
    def generate_audit_dataset(self, num_controls: int = 50, historical_days: int = 30) -> List[Dict[str, Any]]:
        """Generate a complete audit dataset with historical data"""
        results = []
        
        # Generate historical data
        for day in range(historical_days):
            audit_date = datetime.now() - timedelta(days=day)
            
            # Use subset of controls for realistic variation
            controls_for_day = random.sample(self.CONTROL_IDS, min(num_controls, len(self.CONTROL_IDS)))
            
            for control_id in controls_for_day:
                result = self.generate_control_result(control_id, audit_date)
                results.append(result)
        
        return results
    
    def _generate_guid(self) -> str:
        """Generate a realistic GUID"""
        return f"{''.join(random.choices(string.hexdigits.lower(), k=8))}-" \
               f"{''.join(random.choices(string.hexdigits.lower(), k=4))}-" \
               f"{''.join(random.choices(string.hexdigits.lower(), k=4))}-" \
               f"{''.join(random.choices(string.hexdigits.lower(), k=4))}-" \
               f"{''.join(random.choices(string.hexdigits.lower(), k=12))}"


class SharePointDataGenerator:
    """Generate synthetic SharePoint permissions data for performance testing"""
    
    SITE_TYPES = ["Team Site", "Communication Site", "Hub Site", "Document Center"]
    PERMISSION_LEVELS = ["Full Control", "Design", "Edit", "Contribute", "Read", "View Only"]
    USER_TYPES = ["User", "Security Group", "Distribution Group", "SharePoint Group"]
    
    def generate_permission_entry(self, site_index: int) -> Dict[str, str]:
        """Generate a single SharePoint permission entry"""
        site_name = f"Site-{site_index:04d}-{random.choice(['HR', 'Finance', 'IT', 'Marketing', 'Sales'])}"
        site_url = f"https://contoso.sharepoint.com/sites/{site_name.lower().replace(' ', '')}"
        
        # Generate realistic user/group names
        if random.choice([True, False]):
            principal = f"user{random.randint(1, 1000)}@contoso.com"
        else:
            dept = random.choice(['HR', 'Finance', 'IT', 'Marketing', 'Sales'])
            principal = f"{dept}-{random.choice(['Admins', 'Users', 'Contributors'])}"
        
        return {
            "Site Name": site_name,
            "Site URL": site_url,
            "Site Type": random.choice(self.SITE_TYPES),
            "Principal Name": principal,
            "Principal Type": random.choice(self.USER_TYPES),
            "Permission Level": random.choice(self.PERMISSION_LEVELS),
            "Granted Through": random.choice(["Direct", "Group Membership", "Inheritance"]),
            "Created Date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "Last Modified": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        }
    
    def generate_sharepoint_dataset(self, num_sites: int = 100, permissions_per_site: int = 25) -> List[Dict[str, str]]:
        """Generate a complete SharePoint permissions dataset"""
        permissions = []
        
        for site_index in range(1, num_sites + 1):
            for _ in range(random.randint(5, permissions_per_site)):
                permission = self.generate_permission_entry(site_index)
                permissions.append(permission)
        
        return permissions


class PerformanceDataManager:
    """Manages test data creation and cleanup for performance testing"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.temp_dirs = []
        self.cis_generator = M365CISDataGenerator()
        self.sharepoint_generator = SharePointDataGenerator()
    
    def create_test_datasets(self, size_category: str = "medium") -> Dict[str, Path]:
        """Create test datasets of varying sizes"""
        sizes = {
            "small": {"cis_controls": 25, "cis_days": 7, "sp_sites": 50, "sp_perms": 15},
            "medium": {"cis_controls": 50, "cis_days": 30, "sp_sites": 200, "sp_perms": 25},
            "large": {"cis_controls": 100, "cis_days": 90, "sp_sites": 1000, "sp_perms": 50},
            "xlarge": {"cis_controls": 200, "cis_days": 180, "sp_sites": 5000, "sp_perms": 100}
        }
        
        config = sizes.get(size_category, sizes["medium"])
        
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"perf_test_{size_category}_"))
        self.temp_dirs.append(temp_dir)
        
        # Generate CIS audit data
        cis_data = self.cis_generator.generate_audit_dataset(
            num_controls=config["cis_controls"],
            historical_days=config["cis_days"]
        )
        
        cis_file = temp_dir / "m365_cis_audit.json"
        with open(cis_file, 'w', encoding='utf-8') as f:
            json.dump(cis_data, f, indent=2)
        
        # Generate SharePoint permissions data
        sp_data = self.sharepoint_generator.generate_sharepoint_dataset(
            num_sites=config["sp_sites"],
            permissions_per_site=config["sp_perms"]
        )
        
        sp_file = temp_dir / "sharepoint_permissions.csv"
        if sp_data:
            with open(sp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sp_data[0].keys())
                writer.writeheader()
                writer.writerows(sp_data)
        
        return {
            "temp_dir": temp_dir,
            "cis_file": cis_file,
            "sharepoint_file": sp_file,
            "dataset_size": size_category,
            "cis_records": len(cis_data),
            "sharepoint_records": len(sp_data)
        }
    
    def cleanup(self):
        """Clean up temporary test data"""
        import shutil
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self.temp_dirs.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


if __name__ == "__main__":
    # Quick test of data generators
    print("Testing Performance Data Generators...")
    
    with PerformanceDataManager(Path.cwd()) as manager:
        # Test small dataset
        datasets = manager.create_test_datasets("small")
        print(f"Created {datasets['dataset_size']} dataset:")
        print(f"  CIS records: {datasets['cis_records']}")
        print(f"  SharePoint records: {datasets['sharepoint_records']}")
        print(f"  Files in: {datasets['temp_dir']}")
    
    print("Data generators working correctly!")