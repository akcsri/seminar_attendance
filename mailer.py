from flask import render_template, current_app
from flask_mail import Message

def get_direct_formatted_seminar_info(seminar):
    """Get formatted seminar information directly from new columns"""
    if not seminar:
        return {}
    
    return {
        'open_time': seminar.open_time.strftime('%H:%M') if seminar.open_time else '',
        'end_time': seminar.end_time.strftime('%H:%M') if seminar.end_time else '',
        'speaker_bio': seminar.speaker_bio or '',
        'description': seminar.topic or ''
    }

def send_invitation_email(recipient, seminar):
    """Send seminar invitation email to recipient. Does not modify database status."""
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title}のご案内",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    # Get formatted seminar info directly from new columns
    formatted_seminar = get_direct_formatted_seminar_info(seminar)
    msg.html = render_template("email_template.html", 
                              recipient=recipient, 
                              seminar=seminar, 
                              formatted_seminar=formatted_seminar)
    mail.send(msg)

def send_confirmation_email(recipient, seminar):
    """
    Send confirmation email to recipient asking them to confirm attendance.
    
    IMPORTANT: This function ONLY sends an email and does NOT modify attendance status.
    The attendance status should only be changed to 'confirmed' when the recipient
    clicks the confirmation button in the email, which triggers the /confirm endpoint.
    """
    mail = current_app.extensions['mail']
    msg = Message(
        subject=f"{seminar.title} 参加確認",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    # Get formatted seminar info directly from new columns  
    formatted_seminar = get_direct_formatted_seminar_info(seminar)
    msg.html = render_template("confirmation_email_template.html", 
                              recipient=recipient, 
                              seminar=seminar, 
                              formatted_seminar=formatted_seminar)
    mail.send(msg)
    # NOTE: No database modifications should happen here
