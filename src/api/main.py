"""
REST API Endpoints for DDoS Prevention System
FastAPI implementation for system integration
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from typing import List, Optional
from datetime import datetime
import uuid

from src.database.models import init_database
from src.database.database_service import DatabaseService

# Initialize FastAPI application
app = FastAPI(
    title="DDoS Attack Prevention System API",
    description="REST API for DDoS prevention, attack tracking, and user management",
    version="1.0.0"
)

# Database initialization
DATABASE_URL = "sqlite:///./ddos_prevention.db"
engine = init_database(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Get database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/v1/users/register")
def register_user(
    email: str,
    phone_number: str,
    full_name: str,
    country: str,
    region: Optional[str] = None,
    address: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Register a new user in the system"""
    try:
        service = DatabaseService(db)
        
        # Check if user already exists
        if service.get_user_by_email(email):
            raise HTTPException(status_code=400, detail="User already exists")
        
        user_id = str(uuid.uuid4())
        user = service.create_user(
            user_id=user_id,
            email=email,
            phone_number=phone_number,
            full_name=full_name,
            country=country,
            region=region,
            address=address
        )
        
        return {
            "status": "success",
            "user_id": user.user_id,
            "email": user.email,
            "phone": user.phone_number,
            "country": user.country,
            "registration_date": user.registration_date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Retrieve user information"""
    service = DatabaseService(db)
    user = service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "phone": user.phone_number,
        "name": user.full_name,
        "country": user.country,
        "region": user.region,
        "is_flagged": user.is_flagged,
        "flag_reason": user.flag_reason,
        "registration_date": user.registration_date.isoformat()
    }


@app.get("/api/v1/users/search/email")
def search_user_by_email(email: str, db: Session = Depends(get_db)):
    """Search user by email"""
    service = DatabaseService(db)
    user = service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.full_name
    }


@app.get("/api/v1/users/search/phone")
def search_user_by_phone(phone: str, db: Session = Depends(get_db)):
    """Search user by phone number"""
    service = DatabaseService(db)
    user = service.get_user_by_phone(phone)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "phone": user.phone_number,
        "name": user.full_name
    }


@app.put("/api/v1/users/{user_id}/flag")
def flag_user(user_id: str, reason: str, db: Session = Depends(get_db)):
    """Flag a user as suspicious"""
    service = DatabaseService(db)
    
    if not service.flag_user(user_id, reason):
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"status": "success", "message": f"User flagged: {reason}"}


@app.get("/api/v1/users/flagged/list")
def get_flagged_users(db: Session = Depends(get_db)):
    """Get all flagged users"""
    service = DatabaseService(db)
    flagged = service.get_flagged_users()
    
    return {
        "total": len(flagged),
        "users": [
            {
                "user_id": u.user_id,
                "email": u.email,
                "phone": u.phone_number,
                "flag_reason": u.flag_reason
            } for u in flagged
        ]
    }


# ==================== DDoS ACTIVITY ENDPOINTS ====================

@app.post("/api/v1/ddos/report-activity")
def report_ddos_activity(
    user_id: str,
    ip_address: str,
    country: str,
    region: str,
    city: str,
    target_site: str,
    attack_type: str,
    severity: str,
    duration_seconds: int,
    request_count: int,
    machine_hash: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Report a DDoS attack activity"""
    service = DatabaseService(db)
    
    # Verify user exists
    if not service.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    activity_id = str(uuid.uuid4())
    activity = service.create_ddos_activity(
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
    
    return {
        "status": "success",
        "activity_id": activity.activity_id,
        "country": activity.country,
        "ip": activity.ip_address,
        "severity": activity.severity,
        "timestamp": activity.detected_at.isoformat()
    }


@app.get("/api/v1/ddos/country/{country}")
def get_attacks_by_country(country: str, limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    """Get all attacks from a specific country"""
    service = DatabaseService(db)
    attacks = service.get_attacks_by_country(country)[:limit]
    
    return {
        "country": country,
        "total_attacks": len(attacks),
        "attacks": [
            {
                "activity_id": a.activity_id,
                "user_id": a.user_id,
                "ip": a.ip_address,
                "region": a.region,
                "severity": a.severity,
                "timestamp": a.detected_at.isoformat()
            } for a in attacks
        ]
    }


@app.get("/api/v1/ddos/critical")
def get_critical_attacks(limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    """Get all critical severity attacks"""
    service = DatabaseService(db)
    attacks = service.get_critical_attacks()[:limit]
    
    return {
        "severity": "CRITICAL",
        "total_attacks": len(attacks),
        "attacks": [
            {
                "activity_id": a.activity_id,
                "user_id": a.user_id,
                "country": a.country,
                "ip": a.ip_address,
                "timestamp": a.detected_at.isoformat()
            } for a in attacks
        ]
    }


# ==================== CYBER CRIME REPORT ENDPOINTS ====================

@app.post("/api/v1/cybercrime/report")
def create_cyber_crime_report(
    user_id: str,
    country: str,
    cyber_crime_department: str,
    user_name: str,
    user_email: str,
    user_phone: str,
    ip_address: str,
    user_location: str,
    attack_details: str,
    activity_id: Optional[str] = None,
    bank_account_info: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a cyber crime report for submission to authorities"""
    service = DatabaseService(db)
    
    if not service.get_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    report_id = str(uuid.uuid4())
    report = service.create_cyber_crime_report(
        report_id=report_id,
        user_id=user_id,
        country=country,
        cyber_crime_department=cyber_crime_department,
        user_name=user_name,
        user_email=user_email,
        user_phone=user_phone,
        ip_address=ip_address,
        user_location=user_location,
        attack_details=attack_details,
        activity_id=activity_id,
        bank_account_info=bank_account_info
    )
    
    return {
        "status": "success",
        "report_id": report.report_id,
        "country": report.country,
        "submission_status": report.submission_status,
        "created_at": report.created_at.isoformat()
    }


@app.get("/api/v1/cybercrime/country/{country}")
def get_reports_by_country(country: str, limit: int = Query(50, le=100), db: Session = Depends(get_db)):
    """Get all cyber crime reports for a country"""
    service = DatabaseService(db)
    reports = service.get_reports_by_country(country)[:limit]
    
    return {
        "country": country,
        "total_reports": len(reports),
        "reports": [
            {
                "report_id": r.report_id,
                "user_id": r.user_id,
                "ip_address": r.ip_address,
                "submission_status": r.submission_status,
                "created_at": r.created_at.isoformat()
            } for r in reports
        ]
    }


# ==================== HEALTH CHECK ====================

@app.get("/api/v1/health")
def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "api": "DDoS Prevention System API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ==================== ROOT ENDPOINT ====================

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "DDoS Attack Prevention System API",
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "health": "/api/v1/health",
            "users": "/api/v1/users/*",
            "ddos": "/api/v1/ddos/*",
            "cybercrime": "/api/v1/cybercrime/*"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
