"""
Database Models for DDoS Attack Prevention System
SQLAlchemy ORM models for persistent data storage
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """User account information"""
    __tablename__ = "users"
    
    user_id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    region = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    registration_date = Column(DateTime, default=datetime.now(), index=True)
    is_active = Column(Boolean, default=True)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(500), nullable=True)
    
    # Relationships
    browser_licenses = relationship("BrowserLicense", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    ddos_activities = relationship("DDoSActivity", back_populates="user")
    penalties = relationship("Penalty", back_populates="user")


class BrowserLicense(Base):
    """Browser license records"""
    __tablename__ = "browser_licenses"
    
    license_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
    browser_type = Column(String(100), nullable=False)
    installation_id = Column(String(255), unique=True, nullable=False, index=True)
    machine_hash = Column(String(255), nullable=False, index=True)
    installation_path = Column(String(500), nullable=True)
    purchase_date = Column(DateTime, default=datetime.now(), index=True)
    expiry_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="ACTIVE", index=True)  # ACTIVE, SUSPENDED, REVOKED
    cost_paid = Column(Float, default=5000)
    is_valid = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="browser_licenses")
    payments = relationship("Payment", back_populates="browser_license")


class DDoSActivity(Base):
    """DDoS attack activity records"""
    __tablename__ = "ddos_activities"
    
    activity_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    country = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    target_site = Column(String(500), nullable=False, index=True)
    attack_type = Column(String(50), nullable=False)  # DNS, WEBSERVER, BANDWIDTH, COMBINED
    severity = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    duration_seconds = Column(Integer, nullable=False)
    request_count = Column(Integer, nullable=False)
    detected_at = Column(DateTime, default=datetime.now(), index=True)
    is_resolved = Column(Boolean, default=False)
    browser_license_id = Column(String(255), ForeignKey("browser_licenses.license_id"), nullable=True)
    machine_hash = Column(String(255), nullable=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="ddos_activities")
    penalty = relationship("Penalty", uselist=False, back_populates="ddos_activity")


class Penalty(Base):
    """Penalty records for DDoS violations"""
    __tablename__ = "penalties"
    
    penalty_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
    ddos_activity_id = Column(String(255), ForeignKey("ddos_activities.activity_id"), nullable=True)
    reason = Column(String(500), nullable=False)
    amount = Column(Float, default=5000)
    issued_date = Column(DateTime, default=datetime.now(), index=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, PAID, OVERDUE, WAIVED
    is_paid = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="penalties")
    ddos_activity = relationship("DDoSActivity", back_populates="penalty")
    payments = relationship("Payment", back_populates="penalty")


class Payment(Base):
    """Payment records"""
    __tablename__ = "payments"
    
    payment_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
    browser_license_id = Column(String(255), ForeignKey("browser_licenses.license_id"), nullable=True)
    penalty_id = Column(String(255), ForeignKey("penalties.penalty_id"), nullable=True)
    transaction_id = Column(String(255), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # UPI, DEBIT_CARD, CREDIT_CARD, NET_BANKING
    payment_type = Column(String(50), nullable=False)  # PURCHASE, PENALTY, RENEWAL
    payment_date = Column(DateTime, default=datetime.now(), index=True)
    status = Column(String(50), default="SUCCESSFUL", index=True)  # SUCCESSFUL, FAILED, PENDING
    payment_gateway = Column(String(100), nullable=True)
    reference_number = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    browser_license = relationship("BrowserLicense", back_populates="payments")
    penalty = relationship("Penalty", back_populates="payments")


class CyberCrimeReport(Base):
    """Reports submitted to Cyber Crime Department"""
    __tablename__ = "cyber_crime_reports"
    
    report_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False, index=True)
    activity_id = Column(String(255), ForeignKey("ddos_activities.activity_id"), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(2), nullable=True)
    cyber_crime_department = Column(String(255), nullable=False)
    report_description = Column(Text, nullable=False)
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False)
    user_phone = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_location = Column(String(500), nullable=False)
    attack_details = Column(Text, nullable=False)
    bank_account_info = Column(Text, nullable=True)  # Encrypted sensitive data
    evidence_links = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(), index=True)
    submitted_at = Column(DateTime, nullable=True)
    submission_status = Column(String(50), default="DRAFT", index=True)  # DRAFT, SUBMITTED, ACKNOWLEDGED
    government_reference_number = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User")


class AttackStatistics(Base):
    """Aggregated attack statistics"""
    __tablename__ = "attack_statistics"
    
    stat_id = Column(String(255), primary_key=True)
    date = Column(DateTime, default=datetime.now(), index=True)
    country = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=True, index=True)
    total_attacks = Column(Integer, default=0)
    total_attackers = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    average_severity = Column(String(50), nullable=True)
    top_targeted_sites = Column(Text, nullable=True)  # JSON format
    attack_trend = Column(String(50), nullable=True)  # UP, DOWN, STABLE
    
    # Relationships
    user = relationship("User")


class GeoLocation(Base):
    """Geographic location data for attacks"""
    __tablename__ = "geo_locations"
    
    location_id = Column(String(255), primary_key=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    isp = Column(String(255), nullable=True)
    is_vpn = Column(Boolean, default=False)
    is_proxy = Column(Boolean, default=False)
    threat_level = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH
    last_updated = Column(DateTime, default=datetime.now(), index=True)


class AuditLog(Base):
    """System audit log for security and compliance"""
    __tablename__ = "audit_logs"
    
    log_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=True, index=True)
    action = Column(String(255), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, PAYMENT, PENALTY, REPORT
    affected_resource = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.now(), index=True)
    status = Column(String(50), default="SUCCESS", index=True)  # SUCCESS, FAILURE, WARNING


# Database initialization function
def init_database(database_url: str = "sqlite:///ddos_prevention.db"):
    """
    Initialize database with SQLAlchemy
    
    Args:
        database_url: Database connection string
        Example: "sqlite:///ddos_prevention.db"
        Example: "postgresql://user:password@localhost/dbname"
        Example: "mysql+pymysql://user:password@localhost/dbname"
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
