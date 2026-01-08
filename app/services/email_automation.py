"""
Background tasks for email automation
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.services.email import email_service


async def send_upgrade_promotions():
    """Send upgrade promotions to FREE users who haven't upgraded"""
    db = SessionLocal()
    try:
        # Get FREE users who registered 3+ days ago
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        free_users = db.query(User).filter(
            User.subscription_plan == "free",
            User.created_at <= three_days_ago,
            User.is_verified == True
        ).all()
        
        for user in free_users:
            # Check if user has created QR codes
            if user.qr_codes and len(user.qr_codes) > 0:
                await email_service.send_upgrade_promotion(
                    to_email=user.email,
                    user_name=user.full_name or user.email
                )
                print(f"[EMAIL] Sent upgrade promo to {user.email}")
                await asyncio.sleep(2)  # Rate limiting
                
    finally:
        db.close()


async def send_abandoned_cart_emails():
    """Send emails to users who visited pricing but didn't upgrade"""
    # This would track users who visited /pricing page
    # For now, we'll send to FREE users who have hit their QR limit
    db = SessionLocal()
    try:
        free_users = db.query(User).filter(
            User.subscription_plan == "free"
        ).all()
        
        for user in free_users:
            # Check if user has reached QR limit
            if user.qr_codes and len(user.qr_codes) >= 3:
                await email_service.send_abandoned_cart_email(
                    to_email=user.email,
                    user_name=user.full_name or user.email,
                    plan="PRO"
                )
                print(f"[EMAIL] Sent abandoned cart email to {user.email}")
                await asyncio.sleep(2)
                
    finally:
        db.close()


async def send_monthly_reports():
    """Send monthly analytics reports to all users"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_verified == True).all()
        
        for user in users:
            if not user.qr_codes or len(user.qr_codes) == 0:
                continue
                
            # Calculate stats
            total_qr = len(user.qr_codes)
            total_scans = sum(len(qr.scans) for qr in user.qr_codes)
            
            # Scans this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_scans = 0
            for qr in user.qr_codes:
                month_scans += len([s for s in qr.scans if s.scanned_at >= month_start])
            
            stats = {
                "total_qr": total_qr,
                "total_scans": total_scans,
                "month_scans": month_scans
            }
            
            await email_service.send_monthly_report(
                to_email=user.email,
                user_name=user.full_name or user.email,
                stats=stats
            )
            print(f"[EMAIL] Sent monthly report to {user.email}")
            await asyncio.sleep(2)
            
    finally:
        db.close()


# Scheduler function (to be called by a cron job or task scheduler)
async def run_email_campaigns():
    """Run all email campaigns"""
    print("[EMAIL CAMPAIGNS] Starting...")
    
    print("[EMAIL CAMPAIGNS] Sending upgrade promotions...")
    await send_upgrade_promotions()
    
    print("[EMAIL CAMPAIGNS] Sending abandoned cart emails...")
    await send_abandoned_cart_emails()
    
    print("[EMAIL CAMPAIGNS] Complete!")


async def run_monthly_reports():
    """Run monthly reports (should be called on 1st of each month)"""
    print("[MONTHLY REPORTS] Starting...")
    await send_monthly_reports()
    print("[MONTHLY REPORTS] Complete!")


if __name__ == "__main__":
    # For testing
    asyncio.run(run_email_campaigns())
