#!/usr/bin/env python3
"""
Standalone cron job script for sending confirmation emails.

This script is designed to run as a cron job in Render environment.
It sends confirmation emails to attendees 15 minutes before seminar start.

Usage:
    python3 send_confirmation_emails_cron.py

For Render cron job, add this to your cron schedule:
    */1 * * * * cd /opt/render/project/src && python3 send_confirmation_emails_cron.py
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and mailer
from models import db, Seminar, Attendance, Recipient
from mailer import send_confirmation_email
from config import Config

def create_app():
    """Create Flask application with necessary configuration."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail = Mail(app)
    
    return app

def load_sent_emails_cache():
    """Load sent emails cache from file to prevent cross-environment duplicates."""
    cache_file = '/tmp/confirmation_emails_sent.txt'
    sent_emails = set()
    
    try:
        if os.path.exists(cache_file):
            # Only load entries from today to prevent old data accumulation
            today = datetime.utcnow() + timedelta(hours=9).strftime('%Y-%m-%d')
            with open(cache_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(today):
                        # Format: YYYY-MM-DD:seminar_id_recipient_id
                        email_key = line.split(':', 1)[1] if ':' in line else line
                        sent_emails.add(email_key)
    except Exception as e:
        print(f"⚠️ Warning: Could not load sent emails cache: {e}")
    
    return sent_emails

def save_sent_email_to_cache(email_key):
    """Save sent email to cache file for cross-environment duplicate prevention."""
    cache_file = '/tmp/confirmation_emails_sent.txt'
    today = datetime.utcnow() + timedelta(hours=9).strftime('%Y-%m-%d')
    
    try:
        with open(cache_file, 'a') as f:
            f.write(f"{today}:{email_key}\n")
    except Exception as e:
        print(f"⚠️ Warning: Could not save to sent emails cache: {e}")

def cleanup_old_cache_entries():
    """Clean up old cache entries to prevent file from growing too large."""
    cache_file = '/tmp/confirmation_emails_sent.txt'
    
    try:
        if not os.path.exists(cache_file):
            return
            
        today = datetime.utcnow() + timedelta(hours=9).strftime('%Y-%m-%d')
        yesterday = (datetime.utcnow() + timedelta(hours=9) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Read all lines and keep only today's and yesterday's entries
        with open(cache_file, 'r') as f:
            lines = f.readlines()
        
        valid_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith(today) or line.startswith(yesterday):
                valid_lines.append(line + '\n')
        
        # Write back only valid entries
        with open(cache_file, 'w') as f:
            f.writelines(valid_lines)
            
        print(f"🧹 Cleaned up old cache entries, kept {len(valid_lines)} recent entries")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not cleanup cache: {e}")

def send_confirmation_emails_cron():
    """
    Send confirmation emails to attendees 15 minutes before seminar start.
    This is the standalone version of scheduler.py's function for cron job usage.
    """
    app = create_app()
    
    with app.app_context():
        print(f"🕐 Starting confirmation email cron job at {datetime.utcnow() + timedelta(hours=9)}")
        
        # Load cross-environment duplicate prevention cache
        sent_emails_cache = load_sent_emails_cache()
        
        now = datetime.utcnow() + timedelta(hours=9)
        
        # Target seminars starting in 14-16 minutes (2-minute window around 15 minutes)
        start_window = now + timedelta(minutes=14)
        end_window = now + timedelta(minutes=16)
        
        # Find seminars starting within the target window
        upcoming = Seminar.query.filter(
            Seminar.date >= start_window,
            Seminar.date <= end_window
        ).all()
        
        if not upcoming:
            print("📭 No seminars starting in 15 minutes")
            return
        
        total_sent = 0
        total_errors = 0
        total_skipped = 0
        
        for seminar in upcoming:
            print(f"🎯 Processing seminar: '{seminar.title}' (starts: {seminar.date})")
            
            # Only send to 'attend' status to prevent duplicates
            attendees = Attendance.query.filter_by(
                seminar_id=seminar.id, 
                status='attend'
            ).all()
            
            seminar_sent = 0
            seminar_skipped = 0
            
            for attendee in attendees:
                recipient = db.session.get(Recipient, attendee.recipient_id)
                if recipient:
                    # Create unique key to prevent duplicate emails
                    email_key = f"{seminar.id}_{recipient.id}"
                    
                    # Check both session and cross-environment cache
                    if email_key in sent_emails_cache:
                        print(f"⏭️ Skipping {recipient.email} - already sent today")
                        seminar_skipped += 1
                        total_skipped += 1
                        continue
                    
                    try:
                        # Send confirmation email but do NOT change status
                        send_confirmation_email(recipient, seminar)
                        
                        # Mark as sent in cross-environment cache
                        save_sent_email_to_cache(email_key)
                        sent_emails_cache.add(email_key)
                        
                        print(f"✅ Confirmation email sent to {recipient.email}")
                        seminar_sent += 1
                        total_sent += 1
                        
                    except Exception as e:
                        print(f"❌ Failed to send confirmation email to {recipient.email}: {e}")
                        total_errors += 1
                        continue
            
            if seminar_sent > 0 or seminar_skipped > 0:
                print(f"📧 Seminar '{seminar.title}': {seminar_sent} sent, {seminar_skipped} skipped")
        
        print(f"📊 Summary: {total_sent} sent, {total_skipped} skipped, {total_errors} errors")
        
        # Cleanup old cache entries
        if total_sent > 0:
            cleanup_old_cache_entries()

if __name__ == '__main__':
    try:
        send_confirmation_emails_cron()
    except Exception as e:
        print(f"💥 Cron job failed with error: {e}")
        sys.exit(1)