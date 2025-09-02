#!/usr/bin/env python3
"""
Test script to add a seminar with precise timing to test the scheduler.
This will add a seminar exactly 15 minutes from now to test the window logic.
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

def add_precisely_timed_seminar():
    """Add a seminar that starts exactly 15 minutes from now"""
    with app.app_context():
        # Calculate exactly 15 minutes from now
        now = datetime.now()
        future_time = now + timedelta(minutes=15, seconds=30)  # Add 30 seconds buffer
        
        print(f"Current time: {now}")
        print(f"Seminar will start at: {future_time}")
        print(f"Scheduler should trigger when current time is: {future_time - timedelta(minutes=15)}")
        print(f"Target window will be: {future_time - timedelta(minutes=1)} to {future_time + timedelta(minutes=1)}")
        
        # Create a new seminar
        seminar = Seminar(
            title="Precisely Timed Test Seminar",
            date=future_time,
            venue="Test Venue",
            speaker="Test Speaker",
            topic="Testing precise timing for confirmation emails",
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
                comment='Test attendance for precise confirmation email timing'
            )
            db.session.add(attendance)
            db.session.commit()
            
            print(f"Created attendance record for {recipient.name} ({recipient.email})")
            print(f"Status: {attendance.status}")
            
            return seminar.id, recipient.email, future_time
        else:
            print("No recipients found!")
            return None, None, None

if __name__ == '__main__':
    seminar_id, recipient_email, start_time = add_precisely_timed_seminar()
    if seminar_id:
        print(f"\n✅ Setup complete!")
        print(f"📧 Seminar ID: {seminar_id}")
        print(f"👤 Recipient: {recipient_email}")
        print(f"⏰ Start time: {start_time}")
        print(f"🎯 The scheduler should send a confirmation email in about 30 seconds")