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
    msg = Message(subject=f"{seminar.title} 参加確認",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.body = "会場に到着されたら「確認」ボタンをクリックしてください。"
    msg.html = f'<a href="http://localhost:5000/confirm?seminar_id={seminar.id}&recipient_id={recipient.id}">確認</a>'
    mail.send(msg)