"""
Email Service with SendGrid - Complete Implementation
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional
from jinja2 import Template
from datetime import datetime
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
            print(f"[EMAIL SIMULATION] To: {to_email} | Subject: {subject}")
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
    
    async def send_verification_email(self, to_email: str, user_name: str, verification_token: str) -> bool:
        """Send email verification"""
        verification_url = f"{settings.FRONTEND_URL}/verify?token={verification_token}"
        
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4F46E5;">Verifica il tuo account</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Clicca sul pulsante qui sotto per verificare il tuo indirizzo email:</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ verification_url }}" 
                   style="background: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Verifica Account
                </a>
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Oppure copia questo link nel browser:<br>
                <code style="background: #f3f4f6; padding: 8px; display: block; margin-top: 10px;">{{ verification_url }}</code>
            </p>
            
            <p style="color: #999; font-size: 12px;">
                Se non hai richiesto questa verifica, ignora questa email.
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            verification_url=verification_url
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="✉️ Verifica il tuo account QR Code Pro",
            html_content=html
        )
    
    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #EF4444;">Reset Password</h1>
            <p>Hai richiesto il reset della tua password.</p>
            <p>Clicca sul pulsante qui sotto per impostare una nuova password:</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ reset_url }}" 
                   style="background: #EF4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Reset Password
                </a>
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Questo link è valido per 1 ora.
            </p>
            
            <p style="color: #999; font-size: 12px;">
                Se non hai richiesto il reset, ignora questa email. La tua password rimarrà invariata.
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(reset_url=reset_url)
        
        return await self.send_email(
            to_email=to_email,
            subject="🔑 Reset della tua password",
            html_content=html
        )
    
    async def send_abandoned_cart_email(self, to_email: str, user_name: str, plan: str) -> bool:
        """Send abandoned cart reminder"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #F59E0B;">Hai dimenticato qualcosa? 🛒</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Abbiamo notato che eri interessato al piano <strong>{{ plan }}</strong> ma non hai completato l'acquisto.</p>
            
            <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #F59E0B;">
                <h3 style="margin-top: 0;">🎁 Offerta speciale per te!</h3>
                <p style="margin: 0;">Completa l'acquisto ora e ricevi <strong>15% di sconto</strong></p>
                <p style="font-size: 24px; font-weight: bold; color: #F59E0B; margin: 10px 0;">
                    Codice: COMEBACK15
                </p>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ app_url }}/pricing" 
                   style="background: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Completa l'acquisto
                </a>
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Questa offerta è valida per 24 ore.
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            plan=plan.upper(),
            app_url=settings.FRONTEND_URL
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=f"🎁 15% di sconto sul piano {plan.upper()}!",
            html_content=html
        )
    
    async def send_qr_limit_warning(self, to_email: str, user_name: str, current: int, limit: int) -> bool:
        """Send QR limit warning for free users"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #F59E0B;">⚠️ Stai raggiungendo il limite!</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Hai creato <strong>{{ current }}/{{ limit }} QR code</strong> disponibili nel piano FREE.</p>
            
            <div style="background: #EFF6FF; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #1E40AF; margin-top: 0;">Con QR Code PRO:</h3>
                <ul style="color: #1E40AF;">
                    <li>✨ QR code <strong>illimitati</strong></li>
                    <li>📊 Analytics avanzate</li>
                    <li>🎨 Personalizzazione completa</li>
                    <li>🔄 QR dinamici</li>
                </ul>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ app_url }}/pricing" 
                   style="background: #4F46E5; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    Passa a PRO - Solo €9.90/mese
                </a>
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            current=current,
            limit=limit,
            app_url=settings.FRONTEND_URL
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="⚠️ Stai raggiungendo il limite di QR code",
            html_content=html
        )
    
    async def send_monthly_report(self, to_email: str, user_name: str, stats: dict) -> bool:
        """Send monthly analytics report"""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4F46E5;">📊 Report Mensile</h1>
            <p>Ciao {{ user_name }},</p>
            <p>Ecco le statistiche dei tuoi QR code per questo mese:</p>
            
            <div style="background: #F9FAFB; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #E5E7EB;">
                            <strong>QR Code Attivi</strong>
                        </td>
                        <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; text-align: right;">
                            <strong style="color: #4F46E5; font-size: 20px;">{{ stats.total_qr }}</strong>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #E5E7EB;">
                            <strong>Scansioni Totali</strong>
                        </td>
                        <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; text-align: right;">
                            <strong style="color: #10B981; font-size: 20px;">{{ stats.total_scans }}</strong>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;">
                            <strong>Scansioni Questo Mese</strong>
                        </td>
                        <td style="padding: 10px; text-align: right;">
                            <strong style="color: #F59E0B; font-size: 20px;">{{ stats.month_scans }}</strong>
                        </td>
                    </tr>
                </table>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ app_url }}/dashboard" 
                   style="background: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Vedi Report Completo
                </a>
            </p>
        </body>
        </html>
        """
        
        html = Template(template).render(
            user_name=user_name,
            stats=stats,
            app_url=settings.FRONTEND_URL
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=f"📊 Report mensile - {stats['month_scans']} scansioni",
            html_content=html
        )


# Global instance
email_service = EmailService()
