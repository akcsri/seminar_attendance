from app import scheduler
from models import Seminar, Attendance, Recipient
from mailer import send_confirmation_email
from datetime import datetime, timedelta

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    for seminar in upcoming:
        attendees = Attendance.query.filter_by(seminar_id=seminar.id).filter(Attendance.status.in_(['attend', 'pending'])).all()
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            send_confirmation_email(recipient, seminar)