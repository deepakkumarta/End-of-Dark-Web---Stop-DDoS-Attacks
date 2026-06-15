"""
Browser Status Bar Icon Controller
Manages the warning icon display in browser status bar
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Callable


class IconStatus(Enum):
    """Status of the warning icon"""
    NORMAL = "normal"  # Green/inactive
    WARNING = "warning"  # Yellow/blinking
    PENALTY = "penalty"  # Black/solid
    SAFE = "safe"  # Green/inactive


class BrowserStatusBarIcon:
    """Manages the warning icon in browser status bar"""
    
    # Time thresholds
    NORMAL_USAGE_THRESHOLD = 120  # 2 minutes - threshold for unusual activity
    PENALTY_THRESHOLD = 300  # 5 minutes - threshold for issuing penalty
    
    # Icon blink settings
    BLINK_INTERVAL = 0.5  # seconds (blink every 500ms)
    
    def __init__(self, browser_instance_id: str):
        self.browser_instance_id = browser_instance_id
        self.icon_status = IconStatus.NORMAL
        self.is_blinking = False
        self.blink_start_time: Optional[datetime] = None
        self.user_ip: Optional[str] = None
        self.affected_duration: int = 0  # seconds
        self.attack_detected = False
        self.on_icon_click_callback: Optional[Callable] = None
    
    def detect_attack_on_site(self, user_ip: str, duration_seconds: int) -> bool:
        """
        Detect if user is involved in suspicious activity
        
        Args:
            user_ip: IP address of the user
            duration_seconds: Duration of requests to the site
        
        Returns:
            bool: True if suspicious activity detected
        """
        self.user_ip = user_ip
        self.affected_duration = duration_seconds
        self.attack_detected = True
        
        # Check if duration exceeds normal usage threshold (2 minutes)
        if duration_seconds > self.NORMAL_USAGE_THRESHOLD:
            print(f"⚠️ SUSPICIOUS ACTIVITY DETECTED")
            print(f"   User IP: {user_ip}")
            print(f"   Duration: {duration_seconds} seconds")
            print(f"   Activity: Continuous requests to website (unusual pattern)")
            
            # Start warning icon blink
            self.start_warning_blink()
            return True
        
        return False
    
    def start_warning_blink(self) -> bool:
        """Start blinking the warning icon (yellow/orange)"""
        self.icon_status = IconStatus.WARNING
        self.is_blinking = True
        self.blink_start_time = datetime.now()
        
        print(f"\n🔔 STATUS BAR ICON: BLINKING WARNING")
        print(f"   Icon Color: Yellow/Orange (Blinking)")
        print(f"   Message: 'WARNING - Suspicious Activity Detected'")
        print(f"   Interval: {self.BLINK_INTERVAL}s")
        print(f"   Action: Inform user to STOP accessing the website")
        print(f"   Target: All users (innocent users included as precaution)")
        
        return True
    
    def issue_penalty_flag(self, duration_seconds: int) -> bool:
        """
        Issue penalty by changing icon to black
        Called when activity exceeds 5 minutes threshold
        """
        if duration_seconds <= self.PENALTY_THRESHOLD:
            return False
        
        self.icon_status = IconStatus.PENALTY
        self.is_blinking = False
        
        print(f"\n🔴 STATUS BAR ICON: PENALTY ISSUED")
        print(f"   Icon Color: BLACK (Solid, not blinking)")
        print(f"   Duration of Activity: {duration_seconds} seconds ({duration_seconds/60:.1f} minutes)")
        print(f"   Threshold Exceeded: YES (> {self.PENALTY_THRESHOLD} seconds)")
        print(f"   Status: PENALTY - User must pay Rs. 5,000 to continue")
        print(f"   Action: Click icon to proceed to payment")
        
        return True
    
    def handle_icon_click(self) -> str:
        """
        Handle user clicking on the status bar icon
        Redirects to payment page based on current status
        """
        print(f"\n👆 USER CLICKED STATUS BAR ICON")
        
        if self.icon_status == IconStatus.WARNING:
            print(f"   Current Status: WARNING (Yellow)")
            print(f"   Action: Show warning message")
            warning_message = (
                f"⚠️ WARNING ⚠️\n\n"
                f"Unusual Activity Detected!\n\n"
                f"You appear to be continuously accessing a website.\n"
                f"This may be part of a DDoS attack.\n\n"
                f"PLEASE STOP ACCESSING THE WEBSITE IMMEDIATELY.\n\n"
                f"If you continue for more than 5 minutes,\n"
                f"your browser license will be suspended and\n"
                f"you will need to pay Rs. 5,000 to reinstall it."
            )
            print(f"\n{warning_message}")
            return warning_message
        
        elif self.icon_status == IconStatus.PENALTY:
            print(f"   Current Status: PENALTY (Black)")
            print(f"   Action: Redirect to payment portal")
            redirect_url = "https://billing.microsoft.com/DDoS-Penalty-Payment"
            self._redirect_to_payment(redirect_url)
            return redirect_url
        
        return ""
    
    def _redirect_to_payment(self, url: str) -> bool:
        """
        Redirect user to Microsoft billing site for penalty payment
        Simulates browser redirect
        """
        print(f"\n💳 REDIRECTING TO PAYMENT PORTAL")
        print(f"   URL: {url}")
        print(f"   Payment Required: Rs. 5,000")
        print(f"   Payment Methods: UPI, Debit Card, Credit Card, Net Banking")
        print(f"   Purpose: License Reinstatement & Browser Reactivation")
        print(f"   Description: DDoS Attack Participation Penalty")
        print(f"\n   [Opening payment portal in browser...]")
        return True
    
    def check_penalty_status(self, current_duration: int) -> bool:
        """
        Continuously check if user duration exceeds penalty threshold
        """
        if current_duration > self.PENALTY_THRESHOLD:
            if self.icon_status != IconStatus.PENALTY:
                self.issue_penalty_flag(current_duration)
                return True
        
        return False
    
    def reset_icon(self) -> bool:
        """Reset icon to normal state after attack ends"""
        self.icon_status = IconStatus.NORMAL
        self.is_blinking = False
        self.attack_detected = False
        self.affected_duration = 0
        
        print(f"\n✅ STATUS BAR ICON: RESET TO NORMAL")
        print(f"   Icon Color: Green (Normal)")
        print(f"   Message: Cleared")
        print(f"   Status: Safe - All clear")
        
        return True
    
    def get_icon_state(self) -> dict:
        """Get current icon state information"""
        return {
            "browser_instance_id": self.browser_instance_id,
            "icon_status": self.icon_status.value,
            "is_blinking": self.is_blinking,
            "blink_start_time": self.blink_start_time.isoformat() if self.blink_start_time else None,
            "user_ip": self.user_ip,
            "affected_duration": self.affected_duration,
            "attack_detected": self.attack_detected,
            "normal_threshold": self.NORMAL_USAGE_THRESHOLD,
            "penalty_threshold": self.PENALTY_THRESHOLD
        }
