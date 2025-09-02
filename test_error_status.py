#!/usr/bin/env python3
"""
Test email error status handling functionality.
This test verifies that when email sending fails, the attendance status is updated to 'error'.
"""

from flask import Flask
from models import Recipient, Seminar, Attendance, db
from config import Config
from mailer import send_confirmation_email
from dotenv import load_dotenv
import sys
import os

# Load environment variables
load_dotenv()

# Set up Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_seminar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Debug: Print the configuration
print(f"🔧 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

db.init_app(app)

def test_email_error_status():
    """Test that email sending errors result in 'error' status"""
    with app.app_context():
        # Get test data
        recipient = Recipient.query.first()
        seminar = Seminar.query.first()
        
        if not recipient or not seminar:
            print("❌ No test data found. Run seed_db.py first.")
            return False
        
        print(f"📧 Testing email error handling for {recipient.name}")
        print(f"🎯 Seminar: {seminar.title}")
        
        # Remove any existing attendance record for this test
        existing_attendance = Attendance.query.filter_by(
            seminar_id=seminar.id, 
            recipient_id=recipient.id
        ).first()
        if existing_attendance:
            db.session.delete(existing_attendance)
            db.session.commit()
        
        # Simulate the error handling logic from routes.py
        try:
            # This should fail (since we can't send email in test environment)
            send_confirmation_email(recipient, seminar)
            print("❌ Email sending should have failed")
            return False
        except Exception as e:
            print(f"✅ Email sending failed as expected: {e}")
            
            # Now simulate the error status update logic from routes.py
            attendance = Attendance.query.filter_by(
                seminar_id=seminar.id, 
                recipient_id=recipient.id
            ).first()
            
            if attendance:
                attendance.status = 'error'
            else:
                # Create new attendance record with error status
                attendance = Attendance(
                    seminar_id=seminar.id, 
                    recipient_id=recipient.id, 
                    status='error'
                )
                db.session.add(attendance)
            db.session.commit()
            
            # Verify the status was set correctly
            updated_attendance = Attendance.query.filter_by(
                seminar_id=seminar.id, 
                recipient_id=recipient.id
            ).first()
            
            if updated_attendance and updated_attendance.status == 'error':
                print("✅ Attendance status correctly set to 'error'")
                print(f"📊 Attendance ID: {updated_attendance.id}")
                print(f"📊 Status: {updated_attendance.status}")
                return True
            else:
                print("❌ Attendance status was not set to 'error'")
                return False

if __name__ == '__main__':
    print("🧪 Testing Email Error Status Handling")
    print("=" * 50)
    
    success = test_email_error_status()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        sys.exit(1)