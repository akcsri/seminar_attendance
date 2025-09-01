from flask_mail import Message
from flask import render_template
from app import mail
from flask import current_app

def send_invitation_email(recipient, seminar):
    msg = Message(subject=f"{seminar.title}のご案内",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.html = render_template("email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)

def send_confirmation_email(recipient, seminar):
    """Send confirmation email to attendee - does not change attendance status"""
    msg = Message(subject=f"{seminar.title} 参加確認",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.html = render_template("confirmation_email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    # NOTE: Status remains 'attend' - only changes to 'confirmed' when user clicks confirmation button