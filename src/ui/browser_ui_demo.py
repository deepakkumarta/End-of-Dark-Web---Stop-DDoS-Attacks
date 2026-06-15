"""
Browser UI Demonstration
Shows the complete browser UI flow with DDoS protection
"""

from src.ui.BrowserDDoSIntegration import BrowserDDoSIntegration
from src.ui.BrowserLicenseManager import BrowserLicenseManager
from src.models.PenaltySystem import PaymentMethod
import time
import json


def print_header(text: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def demo_browser_ui():
    """Demonstrate browser UI with DDoS protection"""
    
    # Initialize license manager and user
    license_manager = BrowserLicenseManager()
    user_id = "user_deepak@example.com"
    browser_instance_id = "INSTANCE_001"
    
    # STEP 1: Browser Purchase
    print_header("STEP 1: BROWSER PURCHASE")
    print("User buys Internet Explorer from Windows Store")
    print("Price: Rs. 5,000\n")
    
    # Simulate payment
    installation = license_manager.process_payment(
        user_id=user_id,
        payment_amount=5000,
        transaction_id="TXN_PURCHASE_001",
        browser_type="Internet Explorer"
    )
    
    if not installation:
        print("Failed to create installation")
        return
    
    # STEP 2: Browser Startup
    print_header("STEP 2: BROWSER STARTUP")
    browser = BrowserDDoSIntegration(browser_instance_id, user_id)
    
    if not browser.startup_browser(installation):
        print("Failed to start browser")
        return
    
    # STEP 3: Normal Website Browsing
    print_header("STEP 3: NORMAL WEBSITE BROWSING")
    print("User visits a normal website (30 seconds)")
    browser.user_visits_website("https://example.com", "192.168.1.50")
    result = browser.monitor_website_requests("https://example.com", "192.168.1.50", 30)
    print(f"\nResult: {result}")
    
    # STEP 4: Suspicious Activity (2 minutes - exceeds threshold)
    print_header("STEP 4: SUSPICIOUS ACTIVITY DETECTED")
    print("Simulating continuous requests to website for 2.5 minutes")
    print("(This exceeds the 2-minute unusual activity threshold)\n")
    
    result = browser.monitor_website_requests(
        "https://bank-target-site.com",
        "192.168.1.50",
        150  # 2.5 minutes
    )
    print(f"\nResult: {result}")
    
    # Show status bar icon state
    print(f"\nStatus Bar Icon State:")
    print(json.dumps(browser.status_bar_icon.get_icon_state(), indent=2))
    
    # STEP 5: User Clicks Warning Icon
    print_header("STEP 5: USER CLICKS WARNING ICON")
    print("User clicks on the blinking warning icon in status bar\n")
    
    warning_msg = browser.handle_status_bar_icon_click()
    print(f"Message shown to user:\n{warning_msg}")
    
    # STEP 6: Continued Activity (exceeds 5 minute penalty threshold)
    print_header("STEP 6: PENALTY THRESHOLD EXCEEDED")
    print("User ignores warning and continues for 6 minutes (360 seconds)")
    print("(This exceeds the 5-minute penalty threshold)\n")
    
    result = browser.monitor_website_requests(
        "https://bank-target-site.com",
        "192.168.1.50",
        360  # 6 minutes
    )
    print(f"\nResult: {result}")
    
    # Show updated icon state (should be BLACK now)
    print(f"\nUpdated Status Bar Icon State:")
    print(json.dumps(browser.status_bar_icon.get_icon_state(), indent=2))
    
    # STEP 7: User Clicks Black Icon (Penalty Icon)
    print_header("STEP 7: USER CLICKS BLACK PENALTY ICON")
    print("User clicks on the BLACK penalty icon\n")
    
    payment_url = browser.handle_status_bar_icon_click()
    print(f"User redirected to: {payment_url}")
    
    # STEP 8: Payment Processing
    print_header("STEP 8: PAYMENT FOR PENALTY")
    print("User pays Rs. 5,000 penalty to reactivate browser\n")
    
    success = browser.process_penalty_payment(
        PaymentMethod.UPI,
        "TXN_PENALTY_001",
        5000
    )
    
    if success:
        print("\n✅ License reactivated successfully")
    
    # STEP 9: Browser Reactivation
    print_header("STEP 9: BROWSER REACTIVATED")
    print("Browser is now ready to use again\n")
    
    status = browser.get_browser_status()
    print(f"Current browser status:")
    print(f"  Active: {status['is_active']}")
    print(f"  Status Bar Icon: {status['status_bar_icon']['icon_status']}")
    print(f"  Is Blinking: {status['status_bar_icon']['is_blinking']}")
    
    # STEP 10: Browser Uninstall & Reinstall
    print_header("STEP 10: BROWSER UNINSTALL & REINSTALL")
    print("User uninstalls and reinstalls Internet Explorer\n")
    
    browser.handle_uninstall_reinstall("Internet Explorer")
    
    print("\n⚠️  NEW PAYMENT REQUIRED")
    print("   Even after reinstallation, user must pay Rs. 5,000 again")
    print("   This prevents license sharing and piracy")
    
    # STEP 11: System Statistics
    print_header("STEP 11: SYSTEM STATISTICS")
    stats = license_manager.get_system_stats()
    print(json.dumps(stats, indent=2))
    
    # STEP 12: Payment Records
    print_header("STEP 12: PAYMENT RECORDS")
    print(f"Total Payments: {len(license_manager.payment_records)}\n")
    for i, record in enumerate(license_manager.payment_records, 1):
        print(f"Payment {i}:")
        print(f"  Transaction: {record['transaction_id']}")
        print(f"  Amount: Rs. {record['amount']}")
        print(f"  User: {record['user_id']}")
        print(f"  Browser: {record['browser_type']}")
        print()
    
    print_header("DEMONSTRATION COMPLETE")
    print("Browser UI with DDoS protection system fully integrated.\n")


if __name__ == "__main__":
    demo_browser_ui()
