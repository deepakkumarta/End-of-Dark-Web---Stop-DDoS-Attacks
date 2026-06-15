"""
Browser DDoS Prevention UI Integration
Integrates UI components with DDoS detection system
"""

from datetime import datetime, timedelta
from typing import Optional
import sys

from src.ui.BrowserStatusBarIcon import BrowserStatusBarIcon, IconStatus
from src.ui.BrowserLicenseManager import BrowserLicenseManager, BrowserInstallation
from src.core.DDoSDetectionEngine import DDoSDetectionEngine
from src.models.DDoSAttack import DDoSAttack
from src.models.PenaltySystem import PaymentMethod


class BrowserDDoSIntegration:
    """Integrates DDoS detection with browser UI"""
    
    # Thresholds
    SUSPICIOUS_ACTIVITY_THRESHOLD = 120  # 2 minutes
    PENALTY_THRESHOLD = 300  # 5 minutes
    
    def __init__(self, browser_instance_id: str, user_id: str):
        self.browser_instance_id = browser_instance_id
        self.user_id = user_id
        self.status_bar_icon = BrowserStatusBarIcon(browser_instance_id)
        self.license_manager = BrowserLicenseManager()
        self.ddos_engine = DDoSDetectionEngine()
        self.user_activity_log = []
        self.installation: Optional[BrowserInstallation] = None
        self.is_browser_active = False
    
    def startup_browser(self, installation: BrowserInstallation) -> bool:
        """Initialize browser with license check"""
        self.installation = installation
        
        # Validate license
        if not installation.validate_license():
            print(f"\n❌ BROWSER STARTUP FAILED")
            print(f"   Reason: License Invalid or Suspended")
            print(f"   Status: {installation.status.value}")
            print(f"   Action: Cannot start browser")
            return False
        
        # Check if machine is blocked
        if self.license_manager.check_machine_blocked(installation.machine_hash):
            print(f"\n❌ BROWSER BLOCKED")
            print(f"   Machine Hash: {installation.machine_hash}")
            print(f"   Reason: Machine flagged for DDoS violation")
            print(f"   Action: Payment required to unblock")
            return False
        
        self.is_browser_active = True
        print(f"\n✅ BROWSER STARTED SUCCESSFULLY")
        print(f"   Installation: {installation.installation_id[:8]}")
        print(f"   User: {self.user_id}")
        print(f"   Status Bar: Ready")
        
        return True
    
    def user_visits_website(self, website_url: str, user_ip: str) -> bool:
        """
        Log user visiting a website
        Monitor for suspicious activity
        """
        if not self.is_browser_active:
            return False
        
        # Log activity
        activity = {
            "website": website_url,
            "ip": user_ip,
            "timestamp": datetime.now(),
            "action": "visit"
        }
        self.user_activity_log.append(activity)
        
        return True
    
    def monitor_website_requests(self, website_url: str, user_ip: str,
                                duration_seconds: int) -> Optional[dict]:
        """
        Monitor continuous requests to a website
        Detect suspicious/DDoS activity
        """
        if not self.is_browser_active:
            return None
        
        print(f"\n📊 MONITORING WEBSITE REQUESTS")
        print(f"   Website: {website_url}")
        print(f"   User IP: {user_ip}")
        print(f"   Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        
        # Check if duration exceeds normal usage (2 minutes)
        if duration_seconds > self.SUSPICIOUS_ACTIVITY_THRESHOLD:
            print(f"   Status: ⚠️ SUSPICIOUS ACTIVITY DETECTED")
            print(f"   Reason: Continuous requests exceed normal usage pattern")
            
            # Trigger status bar warning icon
            self.status_bar_icon.detect_attack_on_site(user_ip, duration_seconds)
            
            # Show warning to user
            self._show_user_warning()
            
            # Check if exceeds penalty threshold (5 minutes)
            if duration_seconds > self.PENALTY_THRESHOLD:
                print(f"\n   Status: 🔴 PENALTY THRESHOLD EXCEEDED")
                self.status_bar_icon.issue_penalty_flag(duration_seconds)
                self._issue_penalty_and_suspend_license(duration_seconds)
                
                return {
                    "status": "penalty_issued",
                    "duration": duration_seconds,
                    "penalty_amount": 5000
                }
            
            return {
                "status": "warning_issued",
                "duration": duration_seconds,
                "action": "warning_displayed"
            }
        
        return {
            "status": "normal",
            "duration": duration_seconds,
            "action": "no_action"
        }
    
    def _show_user_warning(self) -> bool:
        """Display warning to user"""
        warning_message = (
            "\n" + "="*70 + "\n"
            "⚠️  WARNING - UNUSUAL ACTIVITY DETECTED  ⚠️\n"
            "="*70 + "\n\n"
            "Your browser has detected continuous requests to a website.\n"
            "This activity is unusual and may indicate:\n\n"
            "1. You are part of a DDoS attack\n"
            "2. Malware on your system\n"
            "3. Browser being compromised\n\n"
            "IMMEDIATE ACTION REQUIRED:\n"
            "─────────────────────────\n"
            "❌ STOP accessing the website immediately\n"
            "❌ DO NOT continue making requests\n\n"
            "⏰ Time Limit: 5 minutes maximum\n"
            "💰 Penalty: Rs. 5,000 if you continue beyond 5 minutes\n"
            "🔒 License: Will be SUSPENDED if penalty threshold exceeded\n\n"
            "Click the WARNING ICON in the status bar for more information.\n"
            "="*70 + "\n"
        )
        print(warning_message)
        return True
    
    def _issue_penalty_and_suspend_license(self, duration_seconds: int) -> bool:
        """Issue penalty and suspend license"""
        if not self.installation:
            return False
        
        print(f"\n" + "="*70)
        print(f"🔴 PENALTY ISSUED - LICENSE SUSPENDED 🔴")
        print(f"="*70)
        print(f"\nReason: DDoS Attack Participation")
        print(f"Duration: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        print(f"Exceeded Threshold: {self.PENALTY_THRESHOLD} seconds")
        print(f"Penalty Amount: Rs. 5,000")
        
        # Suspend the license
        self.license_manager.suspend_license_for_penalty(
            self.user_id,
            f"DDoS activity - {duration_seconds}s continuous requests"
        )
        
        # Update installation status
        if self.installation:
            self.installation.suspend_license("DDoS Attack Participation")
        
        # Disable browser
        self.is_browser_active = False
        
        print(f"\n⛔ BROWSER ACCESS DISABLED")
        print(f"   Browser will not function until license is reactivated")
        print(f"   Payment Portal: https://billing.microsoft.com/DDoS-Penalty-Payment")
        
        return True
    
    def handle_status_bar_icon_click(self) -> str:
        """Handle user clicking on status bar warning icon"""
        result = self.status_bar_icon.handle_icon_click()
        
        # If penalty status (black icon), redirect to payment
        if self.status_bar_icon.icon_status == IconStatus.PENALTY:
            self._redirect_to_payment_portal()
        
        return result
    
    def _redirect_to_payment_portal(self) -> bool:
        """Redirect user to payment portal"""
        print(f"\n💳 PAYMENT PORTAL REDIRECT")
        print(f"   URL: https://billing.microsoft.com/DDoS-Penalty-Payment")
        print(f"   Purpose: License Reactivation")
        print(f"   Amount: Rs. 5,000")
        print(f"   Browser: Will be blocked until payment is completed")
        
        return True
    
    def process_penalty_payment(self, payment_method: PaymentMethod,
                               transaction_id: str, amount: float) -> bool:
        """Process penalty payment and reactivate browser"""
        if amount < 5000:
            print(f"❌ Payment failed: Insufficient amount")
            return False
        
        # Reactivate license
        success = self.license_manager.reactivate_after_payment(
            self.user_id,
            amount,
            transaction_id
        )
        
        if success and self.installation:
            # Reactivate browser
            self.installation.status = BrowserInstallation.InstallationStatus.ACTIVE
            self.installation.license_status = "ACTIVE"
            self.is_browser_active = True
            
            print(f"\n✅ BROWSER REACTIVATED")
            print(f"   User: {self.user_id}")
            print(f"   Status: Ready to use")
            
            # Reset warning icon
            self.status_bar_icon.reset_icon()
        
        return success
    
    def handle_uninstall_reinstall(self, browser_type: str = "Internet Explorer") -> None:
        """Handle browser uninstall and reinstall"""
        if not self.installation:
            return
        
        print(f"\n" + "="*70)
        print(f"⚠️  BROWSER UNINSTALL & REINSTALL DETECTED  ⚠️")
        print(f"="*70 + "\n")
        
        # Notify about requirement to pay again
        self.license_manager.handle_uninstall_reinstall(self.user_id, browser_type)
        
        print(f"\nIMPORTANT: Even if you uninstall and reinstall")
        print(f"           {browser_type}, you MUST PAY Rs. 5,000 again.")
        print(f"\nThis prevents license sharing and protects against piracy.")
        
        self.is_browser_active = False
    
    def get_browser_status(self) -> dict:
        """Get current browser status"""
        return {
            "browser_instance_id": self.browser_instance_id,
            "user_id": self.user_id,
            "is_active": self.is_browser_active,
            "installation": self.installation.get_installation_info() if self.installation else None,
            "status_bar_icon": self.status_bar_icon.get_icon_state(),
            "activity_log_count": len(self.user_activity_log),
            "thresholds": {
                "suspicious_activity": self.SUSPICIOUS_ACTIVITY_THRESHOLD,
                "penalty": self.PENALTY_THRESHOLD
            }
        }
