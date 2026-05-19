import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "guide@hanoischoolsreview.com")
SITE_NAME = "Hanoi International Schools Review"


def send_lead_welcome(name: str, email_addr: str, child_age: str) -> None:
    subject = f"Your Free 2026 Hanoi International Schools Guide"
    html = _build_welcome_html(name, child_age)
    _send(email_addr, subject, html)


def send_admin_new_lead(name: str, email_addr: str, child_age: str) -> None:
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if not admin_email:
        return
    subject = f"[{SITE_NAME}] New lead: {name}"
    html = f"""
    <p>A new lead has been captured:</p>
    <ul>
      <li><strong>Name:</strong> {name}</li>
      <li><strong>Email:</strong> {email_addr}</li>
      <li><strong>Child age:</strong> {child_age}</li>
    </ul>
    <p><a href="/admin">View all leads</a></p>
    """
    _send(admin_email, subject, html)


def _send(to: str, subject: str, html: str) -> None:
    if not SMTP_HOST:
        logger.info("[email] SMTP not configured — would send '%s' to %s", subject, to)
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            if SMTP_PORT == 587:
                server.starttls()
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to], msg.as_string())
        logger.info("[email] Sent '%s' to %s", subject, to)
    except Exception as exc:
        logger.error("[email] Failed to send to %s: %s", to, exc)


def _build_welcome_html(name: str, child_age: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body {{ font-family: Arial, sans-serif; color: #1f2937; background: #f5f7fb; margin:0; padding:0; }}
    .wrap {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; }}
    .header {{ background: #0f4c81; color: #fff; padding: 2rem; }}
    .header h1 {{ margin:0; font-size:1.4rem; }}
    .body {{ padding: 2rem; }}
    .cta {{ display:inline-block; background:#16a34a; color:#fff; padding:.75rem 1.5rem; border-radius:6px; text-decoration:none; font-weight:700; }}
    .section {{ border-left: 4px solid #0f4c81; padding: .75rem 1rem; background: #eff6ff; margin: 1rem 0; border-radius: 0 6px 6px 0; }}
    .footer {{ padding: 1.5rem 2rem; background: #f1f5f9; font-size:.8rem; color:#94a3b8; }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>Your Free 2026 Hanoi International Schools Guide</h1>
    <p style="margin:.5rem 0 0; opacity:.85;">From Hanoi International Schools Review</p>
  </div>
  <div class="body">
    <p>Hi {name},</p>
    <p>Thank you for signing up! Here's your quick-start guide to finding the right international school in Hanoi for your child (age group: <strong>{child_age}</strong>).</p>

    <div class="section">
      <strong>Key insight for {child_age} age group:</strong><br/>
      {"Apply early — primary year groups (especially Year 1 and Year 3) fill fast at top schools. Get applications in 6–12 months before your target start date." if "6–10" in child_age or "2–5" in child_age else "For secondary entry, academic records matter most. Request school reports from the last two years and get two strong teacher references ready." if "11–14" in child_age else "For senior school entry, plan your exit pathway first — IB, A-Levels, or AP — then shortlist schools accordingly."}
    </div>

    <h2 style="color:#0f4c81;">Your shortlist checklist</h2>
    <ol>
      <li>Decide on curriculum: <strong>IB, British, American/AP, or French</strong></li>
      <li>Set a realistic budget including transport, uniforms, and meals</li>
      <li>Shortlist by district to keep commute under 30 minutes</li>
      <li>Book school visits for your top 3</li>
      <li>Submit applications — don't wait until the deadline</li>
    </ol>

    <h2 style="color:#0f4c81;">Current scholarship deadlines</h2>
    <p>Several Hanoi schools offer merit scholarships and early-enrolment discounts. Check the latest verified offers on our site before deadlines close.</p>

    <p style="text-align:center; margin-top:2rem;">
      <a class="cta" href="https://hanoischoolsreview.com/hanoi/promotions/">View all active scholarships</a>
    </p>

    <p style="margin-top:2rem; font-size:.9rem; color:#475569;">
      We'll only email you with relevant updates: new scholarship deadlines, guide updates, and school news. You can unsubscribe any time.
    </p>
  </div>
  <div class="footer">
    © 2026 Hanoi International Schools Review. For informational purposes only.
    Always confirm details directly with schools before making decisions.
  </div>
</div>
</body>
</html>
"""
