# 📧 Sistema Email - Guida Configurazione

## Sistema Email Implementato

Il sistema include **8 tipi di email automatiche**:

### ✅ Email Implementate

1. **Welcome Email** 🎉
   - Inviata automaticamente alla registrazione
   - Include link alla dashboard
   - Trigger: Registrazione nuovo utente

2. **Verification Email** ✉️
   - Per verificare l'indirizzo email
   - Include token di verifica
   - Trigger: Registrazione (opzionale)

3. **Upgrade Promotion** 🚀
   - Per utenti FREE dopo 3 giorni
   - Include codice sconto 20%
   - Trigger: Automatico dopo 3 giorni dalla registrazione

4. **QR Limit Warning** ⚠️
   - Quando l'utente FREE crea 2/3 QR
   - Suggerisce upgrade a PRO
   - Trigger: Creazione penultimo QR

5. **Subscription Confirmation** ✅
   - Quando l'utente passa a piano PRO/Business
   - Conferma attivazione abbonamento
   - Trigger: Pagamento Stripe completato

6. **Abandoned Cart** 🛒
   - Per utenti che hanno raggiunto il limite FREE
   - Include sconto 15% (COMEBACK15)
   - Trigger: Script automatico

7. **Password Reset** 🔑
   - Per reset password
   - Include link temporaneo
   - Trigger: Richiesta reset password

8. **Monthly Report** 📊
   - Report statistiche mensili
   - Include QR creati e scansioni
   - Trigger: Script mensile

---

## 🔧 Configurazione SendGrid

### Passo 1: Crea Account SendGrid

1. Vai su https://sendgrid.com/
2. Crea account gratuito (100 email/giorno gratis)
3. Verifica email

### Passo 2: Ottieni API Key

1. Vai su Settings → API Keys
2. Clicca "Create API Key"
3. Nome: `QR-SaaS-Production`
4. Permessi: **Full Access**
5. Copia la API Key (es: `SG.xxx...`)

### Passo 3: Verifica Sender Identity

1. Vai su Settings → Sender Authentication
2. Clicca "Verify a Single Sender"
3. Inserisci la tua email (es: `noreply@tuodominio.com`)
4. Verifica l'email cliccando il link ricevuto

### Passo 4: Configura Railway

Vai su Railway Dashboard → tuo progetto → Variables:

```env
SENDGRID_API_KEY=SG.tuachiavesegreta123...
FROM_EMAIL=noreply@tuodominio.com
FROM_NAME=QR Code Pro
```

### Passo 5: Rideploy

Railway ricompilarà automaticamente con le nuove variabili.

---

## 📨 Test Email

Per testare se le email funzionano:

1. **Registrati sul sito di produzione**
   https://qr-saas-frontend.vercel.app/register.html

2. **Controlla la tua inbox** - Dovresti ricevere la Welcome Email

3. **Crea 2 QR code** - Riceverai QR Limit Warning alla creazione del secondo

---

## 🤖 Email Automation (Background Tasks)

### Script per Campagne Automatiche

```bash
# Nel backend, esegui:
python -m app.services.email_automation
```

Questo script invia:
- ✉️ Upgrade promotions (utenti FREE dopo 3 giorni)
- 🛒 Abandoned cart emails (utenti che hanno raggiunto limite)

### Automazione con Cron Job

**Su Railway**, puoi usare un servizio come **cron-job.org** o **EasyCron**:

1. Crea endpoint API per trigger campagne
2. Schedulalo per eseguire:
   - **Email campaigns**: Ogni giorno alle 10:00
   - **Monthly reports**: 1° di ogni mese alle 9:00

---

## 📊 Email Sending Limits

### SendGrid FREE Tier
- ✅ 100 email/giorno
- ✅ Per sempre
- ✅ Perfetto per iniziare

### Quando Upgradare SendGrid

- Più di 100 utenti attivi/giorno
- Piano PRO SendGrid: $19.95/mese (50,000 email)

---

## 🎨 Personalizzazione Email

I template sono in: `backend/app/services/email.py`

Ogni funzione ha un template HTML personalizzabile:

```python
template = """
<html>
<body style="...">
    <h1>Il tuo titolo</h1>
    <p>Il tuo messaggio con {{ variabili }}</p>
</body>
</html>
"""
```

### Modifica Stili

Puoi cambiare:
- Colori (es: `#4F46E5` → tuo colore brand)
- Font
- Layout
- Immagini (aggiungi logo)

---

## 🚀 Funzionalità Avanzate Future

- [ ] Email con template grafici avanzati
- [ ] A/B testing oggetti email
- [ ] Tracking aperture email
- [ ] Segmentazione utenti
- [ ] Email drip campaigns
- [ ] Newsletter settimanale

---

## 🐛 Troubleshooting

### Email non arrivano?

1. **Controlla spam/junk**
2. **Verifica API Key su Railway**
   ```bash
   railway logs
   # Cerca: [EMAIL SIMULATION] o [EMAIL ERROR]
   ```
3. **Verifica sender su SendGrid**
4. **Controlla quota SendGrid** (100/giorno free)

### Email vanno in spam?

- Verifica dominio con SPF/DKIM su SendGrid
- Usa dominio professionale (non gmail/yahoo)
- Non usare parole spam nell'oggetto

---

## 📱 Contatti

Hai domande? Il sistema è pronto!

**Nota**: Le email sono attualmente in modalità SIMULATION finché non configuri SendGrid. Vedrai i log nel terminale Railway ma le email non verranno inviate realmente.
