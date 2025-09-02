#!/usr/bin/env python3
"""
Test script to add a future seminar and test the scheduler functionality.
This script will add a seminar that starts in about 15 minutes from now.
"""

from flask import Flask
from models import db, Recipient, Seminar, Attendance
from config import Config
from datetime import datetime, timedelta
import os

# Set up local database
os.environ['DATABASE_URL'] = 'sqlite:///local_seminar.db'

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def add_future_seminar():
    """Add a seminar that starts in about 15 minutes"""
    with app.app_context():
        # Calculate a time 15 minutes from now
        now = datetime.now()
        future_time = now + timedelta(minutes=15)
        
        print(f"Current time: {now}")
        print(f"Seminar will start at: {future_time}")
        
        # Create a new seminar
        seminar = Seminar(
            title="Test Confirmation Email Seminar",
            date=future_time,
            venue="Test Venue",
            speaker="Test Speaker",
            topic="Testing automatic confirmation emails",
            contact="test@example.com"
        )
        db.session.add(seminar)
        db.session.commit()
        
        print(f"Created seminar with ID: {seminar.id}")
        
        # Get the first recipient
        recipient = Recipient.query.first()
        if recipient:
            # Create attendance record with 'attend' status
            attendance = Attendance(
                seminar_id=seminar.id,
                recipient_id=recipient.id,
                status='attend',
                comment='Test attendance for confirmation email'
            )
            db.session.add(attendance)
            db.session.commit()
            
            print(f"Created attendance record for {recipient.name} ({recipient.email})")
            print(f"Status: {attendance.status}")
            
            return seminar.id, recipient.email
        else:
            print("No recipients found!")
            return None, None

if __name__ == '__main__':
    seminar_id, recipient_email = add_future_seminar()
    if seminar_id:
        print(f"\n✅ Setup complete!")
        print(f"📧 Seminar ID: {seminar_id}")
        print(f"👤 Recipient: {recipient_email}")
        print(f"⏰ The scheduler should send a confirmation email in about 1-2 minutes")
        print(f"   (when the seminar is 14-16 minutes away)")