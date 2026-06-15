"""
Browser License Manager with DRM
Manages browser license, reinstallation, and DRM protection
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
import hashlib
import uuid


class BrowserInstallation:
    """Represents a browser installation with license tracking"""
    
    class InstallationStatus(Enum):
        ACTIVE = "active"
        SUSPENDED = "suspended"
        REVOKED = "revoked"
        UNINSTALLED = "uninstalled"
    
    def __init__(self, user_id: str, browser_type: str = "Internet Explorer"):
        self.installation_id = str(uuid.uuid4())
        self.user_id = user_id
        self.browser_type = browser_type
        self.install_date = datetime.now()
        self.status = self.InstallationStatus.ACTIVE
        self.machine_hash = self._generate_machine_hash()
        self.license_status = "ACTIVE"
        self.cost_paid = 5000  # Rs.
        self.installation_path = self._get_installation_path()
    
    def _generate_machine_hash(self) -> str:
        """
        Generate a unique hash for the machine
        This hash is tied to the browser installation
        Prevents license sharing across machines
        """
        import platform
        import getpass
        
        machine_info = f"{platform.node()}{getpass.getuser()}{platform.system()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    def _get_installation_path(self) -> str:
        """Get the installation path of the browser"""
        import platform
        
        if platform.system() == "Windows":
            return f"C:\\Program Files\\{self.browser_type}"
        elif platform.system() == "Darwin":  # macOS
            return f"/Applications/{self.browser_type}.app"
        else:  # Linux
            return f"/usr/bin/{self.browser_type.lower()}"
    
    def validate_license(self) -> bool:
        """Validate if license is active for this installation"""
        return self.status == self.InstallationStatus.ACTIVE and self.license_status == "ACTIVE"
    
    def suspend_license(self, reason: str) -> bool:
        """Suspend the license for this installation"""
        self.status = self.InstallationStatus.SUSPENDED
        self.license_status = "SUSPENDED"
        print(f"🔒 LICENSE SUSPENDED for Installation {self.installation_id[:8]}")
        print(f"   Reason: {reason}")
        print(f"   User: {self.user_id}")
        return True
    
    def revoke_installation(self) -> bool:
        """Revoke the installation permanently"""
        self.status = self.InstallationStatus.REVOKED
        self.license_status = "REVOKED"
        print(f"❌ INSTALLATION REVOKED: {self.installation_id[:8]}")
        return True
    
    def get_installation_info(self) -> dict:
        """Get installation information"""
        return {
            "installation_id": self.installation_id,
            "user_id": self.user_id,
            "browser_type": self.browser_type,
            "install_date": self.install_date.isoformat(),
            "status": self.status.value,
            "machine_hash": self.machine_hash,
            "license_status": self.license_status,
            "installation_path": self.installation_path
        }


class BrowserLicenseManager:
    """Manages browser licenses and DRM protection"""
    
    BROWSER_COST = 5000  # Rs.
    
    def __init__(self):
        self.active_installations: dict = {}  # installation_id -> BrowserInstallation
        self.license_registry: dict = {}  # user_id -> [BrowserInstallation]
        self.blocked_machines: dict = {}  # machine_hash -> reason
        self.payment_records: List[dict] = []
    
    def purchase_browser(self, user_id: str, browser_type: str = "Internet Explorer") -> Optional[BrowserInstallation]:
        """
        Purchase and install browser
        Payment of Rs. 5,000 required
        """
        print(f"\n💰 BROWSER PURCHASE INITIATED")
        print(f"   User: {user_id}")
        print(f"   Browser: {browser_type}")
        print(f"   Price: Rs. {self.BROWSER_COST}")
        print(f"   Status: Awaiting Payment...")
        
        return None  # Payment required first
    
    def process_payment(self, user_id: str, payment_amount: float, transaction_id: str,
                       browser_type: str = "Internet Explorer") -> Optional[BrowserInstallation]:
        """
        Process payment and issue license
        """
        if payment_amount < self.BROWSER_COST:
            print(f"❌ PAYMENT FAILED")
            print(f"   Insufficient amount. Required: Rs. {self.BROWSER_COST}, Received: Rs. {payment_amount}")
            return None
        
        # Create installation
        installation = BrowserInstallation(user_id, browser_type)
        
        # Register installation
        self.active_installations[installation.installation_id] = installation
        
        if user_id not in self.license_registry:
            self.license_registry[user_id] = []
        self.license_registry[user_id].append(installation)
        
        # Record payment
        payment_record = {
            "user_id": user_id,
            "transaction_id": transaction_id,
            "amount": payment_amount,
            "browser_type": browser_type,
            "installation_id": installation.installation_id,
            "machine_hash": installation.machine_hash,
            "payment_date": datetime.now().isoformat(),
            "status": "successful"
        }
        self.payment_records.append(payment_record)
        
        print(f"\n✅ BROWSER INSTALLATION SUCCESSFUL")
        print(f"   Installation ID: {installation.installation_id}")
        print(f"   User: {user_id}")
        print(f"   Browser: {browser_type}")
        print(f"   Path: {installation.installation_path}")
        print(f"   Machine Hash: {installation.machine_hash}")
        print(f"   License Status: ACTIVE")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   Amount Paid: Rs. {payment_amount}")
        
        return installation
    
    def handle_uninstall_reinstall(self, user_id: str, browser_type: str = "Internet Explorer") -> bool:
        """
        Handle uninstall and reinstall of browser
        Important: Even after uninstall, user must pay Rs. 5,000 again
        This prevents license sharing and piracy
        """
        print(f"\n⚠️ BROWSER UNINSTALL & REINSTALL DETECTED")
        print(f"   User: {user_id}")
        print(f"   Browser: {browser_type}")
        print(f"   Previous Installations: {len(self.license_registry.get(user_id, []))}")
        
        # Mark previous installations as uninstalled
        if user_id in self.license_registry:
            for installation in self.license_registry[user_id]:
                installation.status = BrowserInstallation.InstallationStatus.UNINSTALLED
                print(f"   Marked old installation as UNINSTALLED: {installation.installation_id[:8]}")
        
        print(f"\n💳 NEW PURCHASE REQUIRED")
        print(f"   Reason: Browser Reinstallation")
        print(f"   Cost: Rs. {self.BROWSER_COST}")
        print(f"   Message: 'You must purchase a new license to reinstall {browser_type}'")
        
        return True
    
    def suspend_license_for_penalty(self, user_id: str, reason: str = "DDoS Attack Participation") -> bool:
        """
        Suspend all active licenses for a user due to penalty
        """
        print(f"\n🔒 SUSPENDING ALL LICENSES FOR USER")
        print(f"   User: {user_id}")
        print(f"   Reason: {reason}")
        
        if user_id in self.license_registry:
            for installation in self.license_registry[user_id]:
                if installation.status == BrowserInstallation.InstallationStatus.ACTIVE:
                    installation.suspend_license(reason)
                    
                    # Block this machine
                    self.blocked_machines[installation.machine_hash] = {
                        "user_id": user_id,
                        "reason": reason,
                        "blocked_date": datetime.now().isoformat()
                    }
        
        print(f"\n💰 PAYMENT REQUIRED FOR REACTIVATION")
        print(f"   Amount: Rs. {self.BROWSER_COST}")
        print(f"   Redirect: https://billing.microsoft.com/DDoS-Penalty-Payment")
        
        return True
    
    def reactivate_after_payment(self, user_id: str, payment_amount: float,
                                transaction_id: str) -> bool:
        """
        Reactivate suspended license after payment
        """
        if payment_amount < self.BROWSER_COST:
            print(f"❌ REACTIVATION FAILED: Insufficient payment")
            return False
        
        print(f"\n✅ LICENSE REACTIVATED")
        print(f"   User: {user_id}")
        print(f"   Amount Paid: Rs. {payment_amount}")
        print(f"   Transaction ID: {transaction_id}")
        
        # Reactivate installations
        if user_id in self.license_registry:
            for installation in self.license_registry[user_id]:
                if installation.status == BrowserInstallation.InstallationStatus.SUSPENDED:
                    installation.status = BrowserInstallation.InstallationStatus.ACTIVE
                    installation.license_status = "ACTIVE"
                    print(f"   ✓ Installation {installation.installation_id[:8]} reactivated")
        
        return True
    
    def check_machine_blocked(self, machine_hash: str) -> bool:
        """
        Check if a machine is blocked from installing browser
        """
        return machine_hash in self.blocked_machines
    
    def get_user_licenses(self, user_id: str) -> List[dict]:
        """Get all licenses for a user"""
        if user_id not in self.license_registry:
            return []
        
        return [inst.get_installation_info() for inst in self.license_registry[user_id]]
    
    def get_system_stats(self) -> dict:
        """Get license system statistics"""
        total_active = sum(1 for inst in self.active_installations.values()
                          if inst.status == BrowserInstallation.InstallationStatus.ACTIVE)
        total_suspended = sum(1 for inst in self.active_installations.values()
                             if inst.status == BrowserInstallation.InstallationStatus.SUSPENDED)
        
        total_revenue = sum(rec['amount'] for rec in self.payment_records)
        
        return {
            "total_installations": len(self.active_installations),
            "active_licenses": total_active,
            "suspended_licenses": total_suspended,
            "blocked_machines": len(self.blocked_machines),
            "total_payments": len(self.payment_records),
            "total_revenue": total_revenue
        }
