from app import scheduler, db
from models import Seminar, Attendance, Recipient
from mail_utils import send_confirmation_email
from datetime import datetime, timedelta

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    for seminar in upcoming:
        # Only send to people who have 'attend' or 'pending' status
        # Don't send to those who already received confirmation emails ('confirmation_sent') or are 'confirmed'
        attendees = Attendance.query.filter_by(seminar_id=seminar.id).filter(Attendance.status.in_(['attend', 'pending'])).all()
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            try:
                send_confirmation_email(recipient, seminar)
                # Update status to 'confirmation_sent' to prevent re-sending emails
                # Only change to 'confirmed' when user clicks the confirmation button
                attendee.status = 'confirmation_sent'
            except Exception as e:
                # Log the error but still update status to avoid repeated attempts
                print(f"Failed to send confirmation email to {recipient.email}: {e}")
                attendee.status = 'confirmation_sent'  # Still mark as sent to avoid spam
        db.session.commit()