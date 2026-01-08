"""
Payment Routes (Stripe Integration)
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.services.stripe_service import stripe_service
from app.services.email import email_service
from app.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


class CheckoutRequest(BaseModel):
    plan: str  # "pro" or "business"


class CheckoutResponse(BaseModel):
    session_id: str
    url: str


@router.post("/create-checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for subscription"""
    
    if checkout_data.plan not in ["pro", "business"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Create checkout session
    session = await stripe_service.create_checkout_session(
        user=current_user,
        plan=checkout_data.plan,
        success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?canceled=true"
    )
    
    # Update user's Stripe customer ID if created
    if not current_user.stripe_customer_id:
        db.commit()
    
    return session


@router.post("/create-portal-session")
async def create_portal_session(
    current_user: User = Depends(get_current_user)
):
    """Create Stripe customer portal session for managing subscription"""
    
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No active subscription found"
        )
    
    portal_url = await stripe_service.create_portal_session(
        user=current_user,
        return_url=f"{settings.FRONTEND_URL}/dashboard"
    )
    
    return {"url": portal_url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe_service.verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Handle different event types
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    if event_type == "checkout.session.completed":
        # Payment successful
        session = event_data
        user_id = session.get("metadata", {}).get("user_id")
        
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                await stripe_service.handle_checkout_completed(session, user)
                db.commit()
                
                # Send confirmation email
                plan = session.get("metadata", {}).get("plan", "PRO")
                await email_service.send_subscription_confirmation(
                    to_email=user.email,
                    plan=plan
                )
    
    elif event_type == "customer.subscription.updated":
        # Subscription updated
        await stripe_service.handle_subscription_updated(event_data)
        db.commit()
    
    elif event_type == "customer.subscription.deleted":
        # Subscription canceled
        subscription_id = event_data["id"]
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        
        if user:
            await stripe_service.handle_subscription_deleted(event_data, user)
            db.commit()
    
    return {"status": "success"}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "FREE",
                "price": 0,
                "currency": "EUR",
                "interval": "month",
                "features": [
                    "3 QR codes",
                    "100 scans/month",
                    "Basic customization",
                    "PNG download"
                ]
            },
            {
                "id": "pro",
                "name": "PRO",
                "price": settings.PLAN_PRO_PRICE,
                "currency": "EUR",
                "interval": "month",
                "features": [
                    "Unlimited QR codes",
                    "Unlimited scans",
                    "Full customization",
                    "Dynamic QR codes",
                    "Advanced analytics",
                    "PNG, SVG, PDF export",
                    "API access"
                ],
                "popular": True
            },
            {
                "id": "business",
                "name": "BUSINESS",
                "price": settings.PLAN_BUSINESS_PRICE,
                "currency": "EUR",
                "interval": "month",
                "features": [
                    "Everything in PRO",
                    "White label",
                    "Team collaboration",
                    "Priority support",
                    "Custom domain",
                    "SLA guarantee"
                ]
            }
        ]
    }
