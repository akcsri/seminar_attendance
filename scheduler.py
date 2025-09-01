from app import scheduler
from models import Seminar, Attendance, Recipient
from mailer import send_confirmation_email
from datetime import datetime, timedelta

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    """
    定期実行: 確認メール送信タスク
    
    セミナー開始15分前以内のセミナーに対して、
    ステータスが 'attend' または 'pending' の参加者に確認メールを送信します。
    
    重要: この関数はメール送信のみを行い、Attendance.statusを変更しません。
    ステータスの更新は受信者が確認ボタンをクリックした時点（/confirmエンドポイント）で行われます。
    """
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    for seminar in upcoming:
        # 'attend' または 'pending' ステータスの参加者にのみ送信
        attendees = Attendance.query.filter_by(seminar_id=seminar.id).filter(Attendance.status.in_(['attend', 'pending'])).all()
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            # メール送信（ステータスは変更されません）
            send_confirmation_email(recipient, seminar)