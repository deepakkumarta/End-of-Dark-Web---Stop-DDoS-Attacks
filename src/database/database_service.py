"""
Database Service Layer
Handles all database operations with abstraction layer
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid

from src.database.models import (
    User, BrowserLicense, DDoSActivity, Penalty, Payment,
    CyberCrimeReport, AttackStatistics, GeoLocation, AuditLog
)


class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user_id: str, email: str, phone_number: str,
                   full_name: str, country: str, region: str = None,
                   address: str = None) -> User:
        """Create a new user in the database"""
        user = User(
            user_id=user_id or str(uuid.uuid4()),
            email=email,
            phone_number=phone_number,
            full_name=full_name,
            country=country,
            region=region,
            address=address
        )
        self.session.add(user)
        self.session.commit()
        self._log_audit("CREATE", "User", user.user_id, f"Created user: {email}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID"""
        return self.session.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email"""
        return self.session.query(User).filter(User.email == email).first()
    
    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Retrieve user by phone number"""
        return self.session.query(User).filter(User.phone_number == phone_number).first()
    
    def flag_user(self, user_id: str, reason: str) -> bool:
        """Flag a user as suspicious"""
        user = self.get_user(user_id)
        if user:
            user.is_flagged = True
            user.flag_reason = reason
            self.session.commit()
            self._log_audit("UPDATE", "User", user_id, f"Flagged user: {reason}")
            return True
        return False
    
    def get_flagged_users(self) -> List[User]:
        """Get all flagged users"""
        return self.session.query(User).filter(User.is_flagged == True).all()
    
    # ==================== BROWSER LICENSE OPERATIONS ====================
    
    def create_browser_license(self, user_id: str, license_id: str,
                             browser_type: str, installation_id: str,
                             machine_hash: str, installation_path: str = None) -> BrowserLicense:
        """Create a browser license record"""
        license_rec = BrowserLicense(
            license_id=license_id,
            user_id=user_id,
            browser_type=browser_type,
            installation_id=installation_id,
            machine_hash=machine_hash,
            installation_path=installation_path
        )
        self.session.add(license_rec)
        self.session.commit()
        self._log_audit("CREATE", "BrowserLicense", license_id, f"Browser: {browser_type}")
        return license_rec
    
    def get_license(self, license_id: str) -> Optional[BrowserLicense]:
        """Get browser license by ID"""
        return self.session.query(BrowserLicense).filter(
            BrowserLicense.license_id == license_id
        ).first()
    
    def get_user_licenses(self, user_id: str) -> List[BrowserLicense]:
        """Get all licenses for a user"""
        return self.session.query(BrowserLicense).filter(
            BrowserLicense.user_id == user_id
        ).all()
    
    def suspend_license(self, license_id: str, reason: str = None) -> bool:
        """Suspend a browser license"""
        license_rec = self.get_license(license_id)
        if license_rec:
            license_rec.status = "SUSPENDED"
            license_rec.is_valid = False
            self.session.commit()
            self._log_audit("UPDATE", "BrowserLicense", license_id, f"License suspended")
            return True
        return False
    
    def get_machine_hash_violations(self, machine_hash: str) -> List[BrowserLicense]:
        """Get all license records for a machine"""
        return self.session.query(BrowserLicense).filter(
            BrowserLicense.machine_hash == machine_hash
        ).all()
    
    # ==================== DDoS ACTIVITY OPERATIONS ====================
    
    def create_ddos_activity(self, activity_id: str, user_id: str,
                           ip_address: str, country: str, region: str,
                           city: str, target_site: str, attack_type: str,
                           severity: str, duration_seconds: int,
                           request_count: int, machine_hash: str = None) -> DDoSActivity:
        """Record a DDoS attack activity"""
        activity = DDoSActivity(
            activity_id=activity_id,
            user_id=user_id,
            ip_address=ip_address,
            country=country,
            region=region,
            city=city,
            target_site=target_site,
            attack_type=attack_type,
            severity=severity,
            duration_seconds=duration_seconds,
            request_count=request_count,
            machine_hash=machine_hash
        )
        self.session.add(activity)
        self.session.commit()
        self._log_audit("CREATE", "DDoSActivity", activity_id, 
                       f"Attack from {ip_address} in {country}")
        return activity
    
    def get_ddos_activity(self, activity_id: str) -> Optional[DDoSActivity]:
        """Get DDoS activity by ID"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.activity_id == activity_id
        ).first()
    
    def get_user_ddos_activities(self, user_id: str) -> List[DDoSActivity]:
        """Get all DDoS activities for a user"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.user_id == user_id
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    def get_attacks_by_country(self, country: str) -> List[DDoSActivity]:
        """Get all attacks originating from a country"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.country == country
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    def get_attacks_by_region(self, region: str) -> List[DDoSActivity]:
        """Get all attacks originating from a region"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.region == region
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    def get_attacks_by_ip(self, ip_address: str) -> List[DDoSActivity]:
        """Get all attacks from a specific IP"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.ip_address == ip_address
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    def get_recent_attacks(self, days: int = 7) -> List[DDoSActivity]:
        """Get attacks from last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.detected_at >= cutoff_date
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    def get_critical_attacks(self) -> List[DDoSActivity]:
        """Get all critical severity attacks"""
        return self.session.query(DDoSActivity).filter(
            DDoSActivity.severity == "CRITICAL"
        ).order_by(desc(DDoSActivity.detected_at)).all()
    
    # ==================== PENALTY OPERATIONS ====================
    
    def create_penalty(self, penalty_id: str, user_id: str,
                      reason: str, amount: float = 5000,
                      ddos_activity_id: str = None) -> Penalty:
        """Create a penalty record"""
        penalty = Penalty(
            penalty_id=penalty_id,
            user_id=user_id,
            ddos_activity_id=ddos_activity_id,
            reason=reason,
            amount=amount,
            due_date=datetime.now() + timedelta(days=7)
        )
        self.session.add(penalty)
        self.session.commit()
        self._log_audit("CREATE", "Penalty", penalty_id, f"Penalty: Rs.{amount}")
        return penalty
    
    def get_penalty(self, penalty_id: str) -> Optional[Penalty]:
        """Get penalty by ID"""
        return self.session.query(Penalty).filter(
            Penalty.penalty_id == penalty_id
        ).first()
    
    def get_user_penalties(self, user_id: str) -> List[Penalty]:
        """Get all penalties for a user"""
        return self.session.query(Penalty).filter(
            Penalty.user_id == user_id
        ).order_by(desc(Penalty.issued_date)).all()
    
    def get_pending_penalties(self, user_id: str) -> List[Penalty]:
        """Get unpaid penalties for a user"""
        return self.session.query(Penalty).filter(
            and_(Penalty.user_id == user_id, Penalty.is_paid == False)
        ).all()
    
    def mark_penalty_paid(self, penalty_id: str) -> bool:
        """Mark penalty as paid"""
        penalty = self.get_penalty(penalty_id)
        if penalty:
            penalty.is_paid = True
            penalty.status = "PAID"
            self.session.commit()
            self._log_audit("UPDATE", "Penalty", penalty_id, "Marked as paid")
            return True
        return False
    
    # ==================== PAYMENT OPERATIONS ====================
    
    def create_payment(self, payment_id: str, user_id: str,
                      transaction_id: str, amount: float,
                      payment_method: str, payment_type: str,
                      browser_license_id: str = None,
                      penalty_id: str = None,
                      reference_number: str = None) -> Payment:
        """Record a payment"""
        payment = Payment(
            payment_id=payment_id,
            user_id=user_id,
            browser_license_id=browser_license_id,
            penalty_id=penalty_id,
            transaction_id=transaction_id,
            amount=amount,
            payment_method=payment_method,
            payment_type=payment_type,
            reference_number=reference_number
        )
        self.session.add(payment)
        self.session.commit()
        self._log_audit("CREATE", "Payment", payment_id, f"Payment: Rs.{amount}")
        return payment
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        return self.session.query(Payment).filter(
            Payment.payment_id == payment_id
        ).first()
    
    def get_user_payments(self, user_id: str) -> List[Payment]:
        """Get all payments by a user"""
        return self.session.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(desc(Payment.payment_date)).all()
    
    def get_total_revenue(self) -> float:
        """Get total revenue from all payments"""
        result = self.session.query(func.sum(Payment.amount)).filter(
            Payment.status == "SUCCESSFUL"
        ).scalar()
        return result or 0.0
    
    # ==================== CYBER CRIME REPORT OPERATIONS ====================
    
    def create_cyber_crime_report(self, report_id: str, user_id: str,
                                 country: str, cyber_crime_department: str,
                                 user_name: str, user_email: str,
                                 user_phone: str, ip_address: str,
                                 user_location: str, attack_details: str,
                                 activity_id: str = None,
                                 bank_account_info: str = None) -> CyberCrimeReport:
        """Create a cyber crime report for submission to authorities"""
        report = CyberCrimeReport(
            report_id=report_id,
            user_id=user_id,
            activity_id=activity_id,
            country=country,
            cyber_crime_department=cyber_crime_department,
            report_description=f"DDoS Attack Report - {attack_details[:100]}",
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            ip_address=ip_address,
            user_location=user_location,
            attack_details=attack_details,
            bank_account_info=bank_account_info
        )
        self.session.add(report)
        self.session.commit()
        self._log_audit("CREATE", "CyberCrimeReport", report_id, 
                       f"Report for {country}")
        return report
    
    def get_cyber_crime_report(self, report_id: str) -> Optional[CyberCrimeReport]:
        """Get cyber crime report by ID"""
        return self.session.query(CyberCrimeReport).filter(
            CyberCrimeReport.report_id == report_id
        ).first()
    
    def get_pending_reports(self) -> List[CyberCrimeReport]:
        """Get all reports pending submission"""
        return self.session.query(CyberCrimeReport).filter(
            CyberCrimeReport.submission_status == "DRAFT"
        ).all()
    
    def submit_cyber_crime_report(self, report_id: str, govt_reference: str) -> bool:
        """Mark report as submitted"""
        report = self.get_cyber_crime_report(report_id)
        if report:
            report.submitted_at = datetime.now()
            report.submission_status = "SUBMITTED"
            report.government_reference_number = govt_reference
            self.session.commit()
            self._log_audit("UPDATE", "CyberCrimeReport", report_id, 
                           f"Submitted with ref: {govt_reference}")
            return True
        return False
    
    def get_reports_by_country(self, country: str) -> List[CyberCrimeReport]:
        """Get all reports for a specific country"""
        return self.session.query(CyberCrimeReport).filter(
            CyberCrimeReport.country == country
        ).order_by(desc(CyberCrimeReport.created_at)).all()
    
    # ==================== GEO LOCATION OPERATIONS ====================
    
    def store_geolocation(self, ip_address: str, country: str,
                         country_code: str = None, region: str = None,
                         city: str = None, latitude: float = None,
                         longitude: float = None, isp: str = None,
                         is_vpn: bool = False, is_proxy: bool = False) -> GeoLocation:
        """Store or update geolocation data"""
        geo = self.session.query(GeoLocation).filter(
            GeoLocation.ip_address == ip_address
        ).first()
        
        if not geo:
            geo = GeoLocation(
                location_id=str(uuid.uuid4()),
                ip_address=ip_address
            )
            self.session.add(geo)
        
        geo.country = country
        geo.country_code = country_code
        geo.region = region
        geo.city = city
        geo.latitude = latitude
        geo.longitude = longitude
        geo.isp = isp
        geo.is_vpn = is_vpn
        geo.is_proxy = is_proxy
        geo.last_updated = datetime.now()
        
        self.session.commit()
        return geo
    
    def get_geolocation(self, ip_address: str) -> Optional[GeoLocation]:
        """Get geolocation for an IP"""
        return self.session.query(GeoLocation).filter(
            GeoLocation.ip_address == ip_address
        ).first()
    
    # ==================== AUDIT LOG OPERATIONS ====================
    
    def _log_audit(self, action: str, resource_type: str, resource_id: str,
                  details: str, user_id: str = None, ip_address: str = None):
        """Log an audit trail entry"""
        log = AuditLog(
            log_id=str(uuid.uuid4()),
            user_id=user_id,
            action=f"{action}: {resource_type}",
            action_type=action,
            affected_resource=f"{resource_type}:{resource_id}",
            details=details,
            ip_address=ip_address
        )
        self.session.add(log)
        self.session.commit()
    
    def get_audit_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        return self.session.query(AuditLog).order_by(
            desc(AuditLog.timestamp)
        ).limit(limit).all()
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_attack_statistics(self, country: str = None, days: int = 7) -> Dict:
        """Get attack statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = self.session.query(DDoSActivity).filter(
            DDoSActivity.detected_at >= cutoff_date
        )
        
        if country:
            query = query.filter(DDoSActivity.country == country)
        
        attacks = query.all()
        
        return {
            "total_attacks": len(attacks),
            "total_duration": sum(a.duration_seconds for a in attacks),
            "total_requests": sum(a.request_count for a in attacks),
            "countries": len(set(a.country for a in attacks)),
            "critical_attacks": len([a for a in attacks if a.severity == "CRITICAL"])
        }
