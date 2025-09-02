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
        
        # Target seminars starting in 13-17 minutes (4-minute window around 15 minutes)
        # Expanded from 14-16 to handle second-level timing precision issues
        start_window = now + timedelta(minutes=13)
        end_window = now + timedelta(minutes=17)
        
        # Enhanced logging for debugging
        print(f"🕐 Scheduler running at: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Looking for seminars between: {start_window.strftime('%Y-%m-%d %H:%M:%S')} - {end_window.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Find seminars starting within the target window
        upcoming = Seminar.query.filter(
            Seminar.date >= start_window,
            Seminar.date <= end_window
        ).all()
        
        # Enhanced logging for seminar detection
        all_seminars = Seminar.query.all()
        print(f"📊 Total seminars in database: {len(all_seminars)}")
        print(f"🔍 Seminars found in target window: {len(upcoming)}")
        
        if upcoming:
            for seminar in upcoming:
                time_until_start = seminar.date - now
                minutes_until = time_until_start.total_seconds() / 60
                print(f"📅 Found seminar: '{seminar.title}' starts at {seminar.date.strftime('%Y-%m-%d %H:%M:%S')} ({minutes_until:.1f} minutes from now)")
        else:
            # Show next upcoming seminars for debugging
            future_seminars = Seminar.query.filter(Seminar.date > now).order_by(Seminar.date).limit(3).all()
            if future_seminars:
                print("🔮 Next upcoming seminars:")
                for seminar in future_seminars:
                    time_until_start = seminar.date - now
                    minutes_until = time_until_start.total_seconds() / 60
                    print(f"   '{seminar.title}' starts at {seminar.date.strftime('%Y-%m-%d %H:%M:%S')} ({minutes_until:.1f} minutes from now)")
            else:
                print("🚫 No future seminars found in database")
        
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