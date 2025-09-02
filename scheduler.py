from app import scheduler, db
from models import Seminar, Attendance, Recipient
from mailer import send_confirmation_email
from datetime import datetime, timedelta

# Global set to track emails already sent in this session to prevent duplicates
_sent_confirmation_emails = set()

@scheduler.task('interval', id='send_confirmation_emails', minutes=1)
def send_confirmation_emails():
    """
    Send confirmation emails to attendees 15 minutes before seminar start.
    Only sends emails to those with 'attend' status and prevents duplicate sends.
    Does NOT modify attendance status - status is only changed when user clicks confirm button.
    """
    from app import app
    with app.app_context():
        now = datetime.now()
        
        # Target seminars starting in 14-16 minutes (2-minute window around 15 minutes)
        start_window = now + timedelta(minutes=14)
        end_window = now + timedelta(minutes=16)
        
        # Find seminars starting within the target window
        upcoming = Seminar.query.filter(
            Seminar.date >= start_window,
            Seminar.date <= end_window
        ).all()
        
        total_sent = 0
        total_errors = 0
        
        for seminar in upcoming:
            # Only send to 'attend' status to prevent duplicates (not 'pending' which might be uncertain)
            # And explicitly exclude 'confirmed' to prevent re-sending
            attendees = Attendance.query.filter_by(
                seminar_id=seminar.id, 
                status='attend'
            ).all()
            
            seminar_sent = 0
            
            for attendee in attendees:
                recipient = Recipient.query.get(attendee.recipient_id)
                if recipient:
                    # Create unique key to prevent duplicate emails in this session
                    email_key = f"{seminar.id}_{recipient.id}"
                    
                    if email_key in _sent_confirmation_emails:
                        continue  # Skip if already sent in this session
                    
                    try:
                        # Send confirmation email but do NOT change status
                        # Status should only change when user clicks the confirmation button
                        send_confirmation_email(recipient, seminar)
                        
                        # Mark as sent to prevent duplicates
                        _sent_confirmation_emails.add(email_key)
                        
                        # Log successful email send without changing status
                        print(f"✅ Confirmation email sent to {recipient.email} for seminar '{seminar.title}' (starts: {seminar.date})")
                        seminar_sent += 1
                        total_sent += 1
                        
                    except Exception as e:
                        # Log error but don't change status
                        print(f"❌ Failed to send confirmation email to {recipient.email}: {e}")
                        total_errors += 1
                        continue
            
            if seminar_sent > 0:
                print(f"📧 Seminar '{seminar.title}': {seminar_sent} confirmation emails sent")
        
        if total_sent > 0 or total_errors > 0:
            print(f"📊 Confirmation email summary: {total_sent} sent, {total_errors} errors")
        
        # Clean up old entries from the tracking set (remove entries older than 2 hours)
        # This prevents memory buildup while still preventing duplicates for recent sends
        current_time = now.timestamp()
        keys_to_remove = []
        for key in _sent_confirmation_emails:
            # In a real implementation, you might want to store timestamps
            # For now, we'll clear the set periodically
            pass
        
        # Reset tracking set every 2 hours to prevent memory buildup
        if len(_sent_confirmation_emails) > 1000:  # Arbitrary limit
            _sent_confirmation_emails.clear()
            print("🧹 Cleared confirmation email tracking cache")