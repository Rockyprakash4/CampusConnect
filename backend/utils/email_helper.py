import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@campusconnect.com")

has_smtp = bool(SMTP_SERVER and SMTP_PORT and SMTP_USERNAME and SMTP_PASSWORD)

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using configured SMTP settings. If credentials are missing,
    logs the email output to the standard console for testing.
    """
    if has_smtp:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = SMTP_FROM
            msg['To'] = to_email
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())
            server.quit()
            print(f"[Email Service] Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"[Email Service] SMTP transmission failed: {e}. Printing to console.")
            
    # Development simulated output
    print("\n" + "="*70)
    print(f"               [CAMPUSCONNECT SIMULATED EMAIL]")
    print(f"To:      {to_email}")
    print(f"Subject: {subject}")
    print("-"*70)
    # Basic HTML cleaner for readable output
    clean = html_content
    for tag in ["<p>", "</p>", "<html>", "</html>", "<body>", "</body>", "<b>", "</b>", "<br>", "</br>"]:
        clean = clean.replace(tag, "\n" if "br" in tag or "/p" in tag else "")
    print(clean.strip())
    print("="*70 + "\n")
    return True

def send_verification_email(to_email: str, username: str, token: str):
    verify_url = f"http://localhost:8000/register.html?token={token}"
    html = f"""
    <p>Welcome to CampusConnect, <b>{username}</b>!</p>
    <p>Please complete your registration by verifying your email address. Click the link below:</p>
    <p><a href="{verify_url}">Verify Email Address</a></p>
    <p>Alternatively, visit: {verify_url}</p>
    <br>
    <p>Regards,<br>CampusConnect Team</p>
    """
    return send_email(to_email, "CampusConnect - Verify Your Email", html)

def send_reset_password_email(to_email: str, username: str, token: str):
    reset_url = f"http://localhost:8000/login.html?reset_token={token}"
    html = f"""
    <p>Hi <b>{username}</b>,</p>
    <p>We received a request to reset your password. Click the link below to configure a new password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>Alternatively, visit: {reset_url}</p>
    <br>
    <p>Regards,<br>CampusConnect Team</p>
    """
    return send_email(to_email, "CampusConnect - Reset Password Request", html)
