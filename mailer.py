from flask import render_template, current_app
from flask_mail import Message
import logging

logger = logging.getLogger(__name__)

def send_invitation_email(recipient, seminar):
    """Send invitation email to recipient for seminar"""
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title}のご案内",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    logger.info(f"Invitation email sent to {recipient.email} for seminar {seminar.title}")

def send_confirmation_email(recipient, seminar):
    """Send confirmation email to recipient for seminar
    
    IMPORTANT: This function should ONLY send email and NOT change attendance status.
    Status should only be changed to 'confirmed' when user clicks the confirmation link.
    """
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title} 参加確認",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("confirmation_email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    logger.info(f"Confirmation email sent to {recipient.email} for seminar {seminar.title}")
    
    # DEFENSIVE: This function should NEVER change attendance status
    # Status should only change when user clicks the confirmation link
