from flask import render_template, current_app
from flask_mail import Message

def send_invitation_email(recipient, seminar):
    """Send seminar invitation email to recipient. Does not modify database status."""
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title}のご案内",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)

def send_confirmation_email(recipient, seminar):
    """
    Send confirmation email to recipient asking them to confirm attendance.
    
    IMPORTANT: This function ONLY sends an email and does NOT modify attendance status.
    The attendance status should only be changed to 'confirmed' when the recipient
    clicks the confirmation button in the email, which triggers the /confirm endpoint.
    """
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title} 参加確認",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("confirmation_email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    # NOTE: No database modifications should happen here
