from app import scheduler, db
from models import Seminar, Attendance, Recipient
from mail_utils import send_confirmation_email
from datetime import datetime, timedelta

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    for seminar in upcoming:
        # Only send to attendees with status 'attend' - don't change their status
        attendees = Attendance.query.filter_by(seminar_id=seminar.id, status='attend').all()
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            if recipient:
                send_confirmation_email(recipient, seminar)
                # Keep status as 'attend' - do not change to 'confirmed'
                # Status should only change to 'confirmed' when user clicks the confirmation button