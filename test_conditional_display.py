#!/usr/bin/env python3
"""Test script for conditional display in email template"""

from app import app, db
from models import Seminar, Recipient
from mailer import get_direct_formatted_seminar_info
from flask import render_template
import datetime

def test_conditional_display():
    """Test email template with empty/None fields"""
    
    with app.app_context():
        # Create a test seminar with some empty fields
        test_seminar = Seminar(
            title="Test Seminar with Empty Fields",
            date=datetime.datetime(2024, 1, 15, 18, 30),  # Has date
            venue="Test Venue",  # Has venue
            speaker=None,  # Empty speaker
            topic=None,  # Empty topic  
            contact="test@example.com",  # Has contact
            open_time=None,  # Empty open_time
            end_time=None,  # Empty end_time
            speaker_bio=None  # Empty speaker_bio
        )
        
        # Create a test recipient
        test_recipient = Recipient(
            name="Test User",
            email="test@example.com",
            affiliation="Test Org",
            phone="123-456-7890"
        )
        
        # Get formatted seminar info 
        formatted_seminar = get_direct_formatted_seminar_info(test_seminar)
        print("Formatted seminar info:", formatted_seminar)
        
        # Render the email template
        html_content = render_template("email_template.html", 
                                     recipient=test_recipient, 
                                     seminar=test_seminar, 
                                     formatted_seminar=formatted_seminar)
        
        # Save rendered HTML to file for inspection
        with open('/tmp/test_email_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Email template rendered successfully!")
        print("Output saved to /tmp/test_email_output.html")
        
        # Check if empty fields are properly hidden
        if 'ゲストスピーカー' not in html_content:
            print("✅ Empty speaker section properly hidden")
        else:
            print("❌ Empty speaker section not hidden")
            
        if '詳細情報' not in html_content:
            print("✅ Empty topic/description section properly hidden")
        else:
            print("❌ Empty topic/description section not hidden")

        # Test with completely empty seminar
        empty_seminar = Seminar(
            title="Empty Test Seminar",
            date=None,
            venue=None,
            speaker=None,
            topic=None,
            contact=None,
            open_time=None,
            end_time=None,
            speaker_bio=None
        )
        
        formatted_empty = get_direct_formatted_seminar_info(empty_seminar)
        html_empty = render_template("email_template.html", 
                                   recipient=test_recipient, 
                                   seminar=empty_seminar, 
                                   formatted_seminar=formatted_empty)
        
        with open('/tmp/test_email_empty.html', 'w', encoding='utf-8') as f:
            f.write(html_empty)
        
        print("Empty seminar template rendered successfully!")
        print("Output saved to /tmp/test_email_empty.html")

if __name__ == "__main__":
    test_conditional_display()