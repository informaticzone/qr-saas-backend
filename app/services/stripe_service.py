"""
Stripe Payment Service
"""
import stripe
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.config import settings
from app.models import User, SubscriptionPlan

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payments and subscriptions"""
    
    def __init__(self):
        self.price_ids = {
            "pro": settings.STRIPE_PRICE_ID_PRO,
            "business": settings.STRIPE_PRICE_ID_BUSINESS,
        }
    
    async def create_customer(self, user: User) -> str:
        """Create Stripe customer for user"""
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name or user.email,
            metadata={
                "user_id": user.id,
            }
        )
        return customer.id
    
    async def create_checkout_session(
        self,
        user: User,
        plan: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """Create Stripe Checkout session for subscription"""
        
        # Ensure user has Stripe customer ID
        if not user.stripe_customer_id:
            customer_id = await self.create_customer(user)
        else:
            customer_id = user.stripe_customer_id
        
        # Get price ID for plan
        price_id = self.price_ids.get(plan)
        if not price_id:
            raise ValueError(f"Invalid plan: {plan}")
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "plan": plan,
            }
        )
        
        return {
            "session_id": session.id,
            "url": session.url,
        }
    
    async def create_portal_session(self, user: User, return_url: str) -> str:
        """Create Stripe customer portal session for managing subscription"""
        if not user.stripe_customer_id:
            raise ValueError("User has no Stripe customer ID")
        
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url,
        )
        
        return session.url
    
    async def handle_checkout_completed(self, session: Dict, user: User) -> None:
        """Handle successful checkout completion"""
        subscription_id = session.get("subscription")
        plan = session.get("metadata", {}).get("plan")
        
        # Update user subscription
        if plan == "pro":
            user.subscription_plan = SubscriptionPlan.PRO
        elif plan == "business":
            user.subscription_plan = SubscriptionPlan.BUSINESS
        
        user.stripe_subscription_id = subscription_id
        
        # Set subscription end date (30 days from now)
        user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
    
    async def handle_subscription_updated(self, subscription: Dict) -> None:
        """Handle subscription update webhook"""
        # This would update user's subscription status in database
        pass
    
    async def handle_subscription_deleted(self, subscription: Dict, user: User) -> None:
        """Handle subscription cancellation"""
        user.subscription_plan = SubscriptionPlan.FREE
        user.stripe_subscription_id = None
        user.subscription_ends_at = None
    
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "eur",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create one-time payment intent (for template purchases)"""
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            metadata=metadata or {},
        )
        
        return {
            "client_secret": intent.client_secret,
            "id": intent.id,
        }
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> Dict:
        """Verify Stripe webhook signature"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")


# Global instance
stripe_service = StripeService()
