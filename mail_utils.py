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
    """
    確認メール送信関数（mail_utils版）
    
    重要: この関数はメール送信のみを行い、Attendance.statusを変更しません。
    ステータスの更新は受信者が確認ボタンをクリックした時点（/confirmエンドポイント）で行われます。
    
    Args:
        recipient: Recipientオブジェクト  
        seminar: Seminarオブジェクト
    """
    msg = Message(subject=f"{seminar.title} 参加確認",
                  sender = current_app.config['MAIL_USERNAME'],
                  recipients=[recipient.email])
    msg.body = "会場に到着されたら「確認」ボタンをクリックしてください。"
    msg.html = f'<a href="https://seminar-attendance.onrender.com/confirm?seminar_id={seminar.id}&recipient_id={recipient.id}">確認</a>'
    mail.send(msg)
    # 注意: ここでAttendance.statusは変更しません