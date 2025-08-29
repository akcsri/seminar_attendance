from flask import render_template, current_app
from flask_mail import Message

def send_invitation_email(recipient, seminar):
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title}のご案内",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)

def send_confirmation_email(recipient, seminar):
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title} 参加確認",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("confirmation_email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
