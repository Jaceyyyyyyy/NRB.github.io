"""
NRB Projects - Flask Backend
Brisbane Construction Company Website
"""

import os
import json
import csv
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, TextAreaField, SelectField, TelField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional
from dotenv import load_dotenv
import bleach

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

# ── App setup ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["WTF_CSRF_ENABLED"] = True
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  # 1 hour token validity

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USER or "no-reply@nrbprojects.com")
NOTIFY_TO = "reece@nrbprojects.com"

# ── Security extensions ──────────────────────────────────────────────────────
csrf = CSRFProtect(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ── Submissions directory ────────────────────────────────────────────────────
SUBMISSIONS_DIR = Path("submissions")
SUBMISSIONS_DIR.mkdir(exist_ok=True)

QUOTES_FILE = SUBMISSIONS_DIR / "quote_requests.csv"
CONTACTS_FILE = SUBMISSIONS_DIR / "contact_messages.csv"

def ensure_csv(filepath, headers):
    """Create CSV with headers if it doesn't exist."""
    if not filepath.exists():
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

ensure_csv(QUOTES_FILE, [
    "timestamp", "name", "email", "phone", "project_type",
    "location", "budget_range", "description"
])
ensure_csv(CONTACTS_FILE, [
    "timestamp", "name", "email", "phone", "message"
])

# ── Sanitisation helper ──────────────────────────────────────────────────────
def clean(text):
    """Strip all HTML tags and limit whitespace."""
    return bleach.clean(str(text), tags=[], strip=True).strip()


def send_submission_email(subject, lines, reply_to=""):
    """Send submission alert email if SMTP is configured."""
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        app.logger.warning("Email not sent: SMTP settings missing.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_FROM
    msg["To"] = NOTIFY_TO
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content("\n".join(lines))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as exc:
        app.logger.exception("Failed to send submission email: %s", exc)
        return False

# ── Forms ────────────────────────────────────────────────────────────────────
PHONE_RE = r"^[\d\s\+\-\(\)]{7,20}$"

class QuoteForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(), Length(min=2, max=100)
    ])
    email = StringField("Email Address", validators=[
        DataRequired(), Email(), Length(max=254)
    ])
    phone = TelField("Phone Number", validators=[
        DataRequired(), Regexp(PHONE_RE, message="Enter a valid phone number")
    ])
    project_type = SelectField("Project Type", validators=[DataRequired()], choices=[
        ("", "Select project type…"),
        ("residential_new", "Residential — New Build"),
        ("residential_reno", "Residential — Renovation / Extension"),
        ("commercial_new", "Commercial — New Build"),
        ("commercial_fit", "Commercial — Fit-Out"),
        ("civil", "Civil / Infrastructure"),
        ("demolition", "Demolition"),
        ("other", "Other"),
    ])
    location = StringField("Project Location (Suburb)", validators=[
        DataRequired(), Length(max=150)
    ])
    budget_range = SelectField("Approximate Budget", choices=[
        ("", "Select budget range…"),
        ("under_50k", "Under $50,000"),
        ("50k_150k", "$50,000 – $150,000"),
        ("150k_500k", "$150,000 – $500,000"),
        ("500k_1m", "$500,000 – $1,000,000"),
        ("1m_plus", "$1,000,000+"),
        ("unsure", "Not sure yet"),
    ])
    description = TextAreaField("Project Description", validators=[
        DataRequired(), Length(min=20, max=2000)
    ])

class ContactForm(FlaskForm):
    name = StringField("Full Name", validators=[
        DataRequired(), Length(min=2, max=100)
    ])
    email = StringField("Email Address", validators=[
        DataRequired(), Email(), Length(max=254)
    ])
    phone = TelField("Phone Number", validators=[
        Optional(), Regexp(PHONE_RE, message="Enter a valid phone number")
    ])
    message = TextAreaField("Message", validators=[
        DataRequired(), Length(min=10, max=2000)
    ])

# ── Sample project data (replace with your real projects) ───────────────────
PROJECTS = [
    {
        "id": 1,
        "title": "project1 placeholder",
        "category": "Residential",
        "location": "location",
        "year": 2026,
        "description": "breif summary...",
        "image": "project1.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
    {
        "id": 2,
        "title": "project2 placeholder",
        "category": "location",
        "location": "Fortitude Valley, Brisbane",
        "year": 2024,
        "description": "breif summary...",
        "image": "project2.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
    {
        "id": 3,
        "title": "project3 placeholder",
        "category": "location",
        "location": "New Farm, Brisbane",
        "year": 2023,
        "description": "breif summary...",
        "image": "project3.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
    {
        "id": 4,
        "title": "project4 placeholder",
        "category": "location",
        "location": "Hendra, Brisbane",
        "year": 2023,
        "description": "breif summary...",
        "image": "project4.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
    {
        "id": 5,
        "title": "project5 placeholder",
        "category": "location",
        "location": "Paddington, Brisbane",
        "year": 2023,
        "description": "breif summary...",
        "image": "project5.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
    {
        "id": 6,
        "title": "project6 placeholder",
        "category": "location",
        "location": "Eagle Farm, Brisbane",
        "year": 2022,
        "description": "breif summary...",
        "image": "project6.jpg",
        "tags": ["tag1", "tag2", "tag3"],
    },
]

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    featured = PROJECTS[:3]
    return render_template("index.html", projects=featured)


@app.route("/projects")
def projects():
    category = request.args.get("category", "all")
    if category != "all":
        filtered = [p for p in PROJECTS if p["category"].lower() == category.lower()]
    else:
        filtered = PROJECTS
    return render_template("projects.html", projects=filtered, active_category=category)


@app.route("/quote", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def quote():
    form = QuoteForm()
    if form.validate_on_submit():
        row = [
            datetime.now().isoformat(),
            clean(form.name.data),
            clean(form.email.data),
            clean(form.phone.data),
            clean(form.project_type.data),
            clean(form.location.data),
            clean(form.budget_range.data),
            clean(form.description.data),
        ]
        with open(QUOTES_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)
        send_submission_email(
            subject="New NRB Quote Request",
            reply_to=row[2],
            lines=[
                "A new quote request was submitted.",
                "",
                f"Timestamp: {row[0]}",
                f"Name: {row[1]}",
                f"Email: {row[2]}",
                f"Phone: {row[3]}",
                f"Project Type: {row[4]}",
                f"Location: {row[5]}",
                f"Budget Range: {row[6]}",
                "",
                "Project Description:",
                row[7],
            ],
        )
        flash("success")
        return redirect(url_for("quote_thanks"))
    return render_template("quote.html", form=form)


@app.route("/quote/thanks")
def quote_thanks():
    return render_template("thanks.html",
        title="Quote Request Received",
        message="Thanks for reaching out. We'll review your project details and be in touch within 1–2 business days."
    )


@app.route("/contact", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        row = [
            datetime.now().isoformat(),
            clean(form.name.data),
            clean(form.email.data),
            clean(form.phone.data or ""),
            clean(form.message.data),
        ]
        with open(CONTACTS_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)
        send_submission_email(
            subject="New NRB Contact Message",
            reply_to=row[2],
            lines=[
                "A new contact message was submitted.",
                "",
                f"Timestamp: {row[0]}",
                f"Name: {row[1]}",
                f"Email: {row[2]}",
                f"Phone: {row[3] or 'Not provided'}",
                "",
                "Message:",
                row[4],
            ],
        )
        flash("success")
        return redirect(url_for("contact_thanks"))
    return render_template("contact.html", form=form)


@app.route("/contact/thanks")
def contact_thanks():
    return render_template("thanks.html",
        title="Message Sent",
        message="Thanks for getting in touch. We'll get back to you as soon as possible."
    )


# ── Security headers ─────────────────────────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ── Error pages ──────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404

@app.errorhandler(429)
def too_many(e):
    return render_template("error.html", code=429, message="Too many requests. Please try again shortly."), 429

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong on our end."), 500


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
