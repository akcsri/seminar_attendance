from flask_mail import Message
from flask import render_template
from app import mail
from flask import current_app
from seminar_utils import get_formatted_seminar_info

def send_invitation_email(recipient, seminar):
    msg = Message(subject=f"{seminar.title}のご案内",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    # Get formatted seminar info with structured data
    formatted_seminar = get_formatted_seminar_info(seminar)
    msg.html = render_template("email_template.html", 
                              recipient=recipient, 
                              seminar=seminar, 
                              formatted_seminar=formatted_seminar)
    mail.send(msg)

def send_confirmation_email(recipient, seminar):
    msg = Message(subject=f"{seminar.title} 参加確認",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    # Get formatted seminar info with structured data
    formatted_seminar = get_formatted_seminar_info(seminar)
    msg.html = render_template("confirmation_email_template.html", 
                              recipient=recipient, 
                              seminar=seminar, 
                              formatted_seminar=formatted_seminar)
    mail.send(msg)