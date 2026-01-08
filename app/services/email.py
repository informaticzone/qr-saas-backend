"""
Email Service
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List, Optional
from jinja2 import Template
from app.config import settings


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else None
        self.from_email = Email(settings.FROM_EMAIL, settings.FROM_NAME)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email"""
        if not self.client:
            print(f"[EMAIL] Would send to {to_email}: {subject}")
            return True
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if text_content:
                message.add_content(Content("text/plain", text_content))
            
            response = self.client.send(message)
            return response.status_code == 202
        
        except Exception as e:
            print(f"[EMAIL ERROR] {str(e)}")
            return False
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4F46E5;">Benvenuto su QR Code Pro!</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Grazie per esserti registrato! Ora puoi creare QR code personalizzati con analytics avanzate.</p>
            
            <h2>Inizia subito:</h2>
            <ul>
                <li>Crea il tuo primo QR code</li>
                <li>Personalizza colori e stile</li>
                <li>Traccia le scansioni in tempo reale</li>
            </ul>
            
            <p>
                <a href="{{ app_url }}/dashboard" 
                   style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Vai alla Dashboard
                </a>
            </p>
            
            <p>Hai domande? Risponda a questa email!</p>
            
            <p>Il team di QR Code Pro</p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            app_url=settings.APP_URL
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="Benvenuto su QR Code Pro! 🎉",
            html_content=html
        )
    
    async def send_upgrade_promotion(self, to_email: str, user_name: str, discount_code: str = "SAVE20") -> bool:
        """Send upgrade promotion email"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4F46E5;">Sblocca tutto il potenziale! 🚀</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Vediamo che stai usando la versione FREE. Ecco cosa ti perdi:</p>
            
            <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Con QR Code PRO:</h3>
                <ul>
                    <li>✅ QR code <strong>illimitati</strong></li>
                    <li>✅ Analytics dettagliate in tempo reale</li>
                    <li>✅ Personalizzazione completa (colori, logo, stili)</li>
                    <li>✅ QR dinamici (cambia URL senza rigenerare)</li>
                    <li>✅ Export in PNG, SVG, PDF</li>
                </ul>
            </div>
            
            <p style="background: #FEF3C7; padding: 15px; border-left: 4px solid #F59E0B;">
                <strong>Offerta speciale:</strong> Usa il codice <code style="background: white; padding: 4px 8px;">{{ discount_code }}</code> per <strong>20% di sconto</strong> sul primo mese!
            </p>
            
            <p>
                <a href="{{ app_url }}/pricing" 
                   style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Passa a PRO - Solo €7.92/mese
                </a>
            </p>
            
            <p><small>Offerta valida per 7 giorni</small></p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            app_url=settings.APP_URL,
            discount_code=discount_code
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=f"🎁 20% di sconto su QR Code PRO!",
            html_content=html
        )
    
    async def send_subscription_confirmation(self, to_email: str, plan: str) -> bool:
        """Send subscription confirmation email"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #10B981;">Abbonamento Attivato! ✅</h1>
            <p>Il tuo abbonamento <strong>{{ plan }}</strong> è ora attivo.</p>
            <p>Ora hai accesso a tutte le funzionalità premium!</p>
            
            <p>
                <a href="{{ app_url }}/dashboard" 
                   style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Vai alla Dashboard
                </a>
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            plan=plan.upper(),
            app_url=settings.APP_URL
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="Abbonamento attivato!",
            html_content=html
        )


# Global instance
email_service = EmailService()
