from app import scheduler
from models import Seminar, Attendance, Recipient
from mail_utils import send_confirmation_email
from datetime import datetime, timedelta
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    now = datetime.now()
    upcoming = Seminar.query.filter(Seminar.date <= now + timedelta(minutes=15)).all()
    
    for seminar in upcoming:
        attendees = Attendance.query.filter_by(seminar_id=seminar.id).filter(Attendance.status.in_(['attend', 'pending'])).all()
        
        for attendee in attendees:
            recipient = Recipient.query.get(attendee.recipient_id)
            if recipient:
                # Log the status before sending email
                original_status = attendee.status
                logger.info(f"Sending confirmation email to {recipient.email} for seminar {seminar.id}. Current status: {original_status}")
                
                try:
                    send_confirmation_email(recipient, seminar)
                    logger.info(f"Confirmation email sent successfully to {recipient.email}")
                    
                    # DEFENSIVE: Ensure status hasn't changed automatically after sending email
                    # Refresh the attendance record to check for any unexpected changes
                    from models import db
                    db.session.refresh(attendee)
                    
                    if attendee.status != original_status:
                        logger.warning(f"BUG DETECTED: Status changed from {original_status} to {attendee.status} after sending email! Reverting...")
                        # Revert the status back to original
                        attendee.status = original_status
                        db.session.commit()
                        logger.info(f"Status reverted back to {original_status}")
                    else:
                        logger.info(f"Status correctly remained as {attendee.status} after sending email")
                        
                except Exception as e:
                    logger.error(f"Error sending confirmation email to {recipient.email}: {e}")
            else:
                logger.warning(f"Recipient not found for attendance ID {attendee.id}")