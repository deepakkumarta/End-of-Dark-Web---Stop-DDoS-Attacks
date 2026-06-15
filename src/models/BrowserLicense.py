"""
Browser License Model
Manages browser purchase, licensing, and penalty system
"""

from enum import Enum
from datetime import datetime
from typing import Optional


class BrowserLicense:
    """Represents a browser license for DDoS prevention system"""
    
    BROWSER_LICENSE_COST = 5000  # Rs.
    PENALTY_COST = 5000  # Rs.
    
    class LicenseStatus(Enum):
        ACTIVE = "active"
        SUSPENDED = "suspended"
        EXPIRED = "expired"
        REVOKED = "revoked"
    
    def __init__(self, user_id: str, purchase_date: datetime = None):
        self.user_id = user_id
        self.license_id = self._generate_license_id()
        self.purchase_date = purchase_date or datetime.now()
        self.status = self.LicenseStatus.ACTIVE
        self.cost_paid = self.BROWSER_LICENSE_COST
        self.is_valid = True
    
    def _generate_license_id(self) -> str:
        """Generate unique license ID"""
        import uuid
        return str(uuid.uuid4())
    
    def is_active(self) -> bool:
        """Check if license is currently active"""
        return self.status == self.LicenseStatus.ACTIVE and self.is_valid
    
    def suspend_license(self, reason: str) -> bool:
        """Suspend the license"""
        self.status = self.LicenseStatus.SUSPENDED
        self.is_valid = False
        print(f"License {self.license_id} suspended. Reason: {reason}")
        return True
    
    def revoke_license(self) -> bool:
        """Revoke the license permanently"""
        self.status = self.LicenseStatus.REVOKED
        self.is_valid = False
        print(f"License {self.license_id} revoked permanently.")
        return True
    
    def renew_license(self) -> bool:
        """Renew a suspended license"""
        if self.status == self.LicenseStatus.SUSPENDED:
            self.status = self.LicenseStatus.ACTIVE
            self.is_valid = True
            print(f"License {self.license_id} renewed.")
            return True
        return False
    
    def get_license_info(self) -> dict:
        """Get license information"""
        return {
            "license_id": self.license_id,
            "user_id": self.user_id,
            "purchase_date": self.purchase_date.isoformat(),
            "status": self.status.value,
            "cost_paid": self.cost_paid,
            "is_valid": self.is_valid
        }
