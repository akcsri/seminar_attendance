from flask_mail import Message
from flask import render_template
from app import mail
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def send_invitation_email(recipient, seminar):
    """Send invitation email to recipient for seminar"""
    msg = Message(subject=f"{seminar.title}のご案内",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.html = render_template("email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    logger.info(f"Invitation email sent to {recipient.email} for seminar {seminar.title}")

def send_confirmation_email(recipient, seminar):
    """Send confirmation email to recipient for seminar
    
    IMPORTANT: This function should ONLY send email and NOT change attendance status.
    Status should only be changed to 'confirmed' when user clicks the confirmation link.
    """
    msg = Message(subject=f"{seminar.title} 参加確認",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.body = "会場に到着されたら「確認」ボタンをクリックしてください。"
    msg.html = f'<a href="https://seminar-attendance.onrender.com/confirm?seminar_id={seminar.id}&recipient_id={recipient.id}">確認</a>'
    mail.send(msg)
    logger.info(f"Confirmation email sent to {recipient.email} for seminar {seminar.title}")
    
    # DEFENSIVE: This function should NEVER change attendance status
    # Status should only change when user clicks the confirmation link