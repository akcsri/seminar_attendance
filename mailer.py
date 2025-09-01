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
    """
    確認メール送信関数
    
    重要: この関数はメール送信のみを行い、Attendance.statusを変更しません。
    ステータスの更新は受信者が確認ボタンをクリックした時点（/confirmエンドポイント）で行われます。
    
    Args:
        recipient: Recipientオブジェクト
        seminar: Seminarオブジェクト
    """
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title} 参加確認",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template("confirmation_email_template.html", recipient=recipient, seminar=seminar)
    mail.send(msg)
    # 注意: ここでAttendance.statusは変更しません
