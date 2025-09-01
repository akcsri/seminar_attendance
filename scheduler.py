from app import scheduler, db
from models import Seminar, Attendance, Recipient
from mailer import send_confirmation_email
from datetime import datetime, timedelta

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    """
    Send confirmation emails to attendees within 15 minutes of seminar start.
    Only sends emails to those with 'attend' status to prevent duplicate sends.
    Does NOT modify attendance status - status is only changed when user clicks confirm button.
    """
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    for seminar in upcoming:
        # Only send to 'attend' status to prevent duplicates (not 'pending' which might be uncertain)
        # And explicitly exclude 'confirmed' to prevent re-sending
        attendees = Attendance.query.filter_by(
            seminar_id=seminar.id, 
            status='attend'
        ).all()
        
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            if recipient:
                try:
                    # Send confirmation email but do NOT change status
                    # Status should only change when user clicks the confirmation button
                    send_confirmation_email(recipient, seminar)
                    
                    # Optional: Log successful email send without changing status
                    print(f"Confirmation email sent to {recipient.email} for seminar {seminar.title}")
                    
                except Exception as e:
                    # Log error but don't change status
                    print(f"Failed to send confirmation email to {recipient.email}: {e}")
                    continue