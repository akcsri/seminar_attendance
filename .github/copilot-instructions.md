# Seminar Attendance Management System

The seminar attendance management system is a Python Flask web application that manages seminar registrations, sends email invitations, tracks attendance responses, and provides an admin dashboard for managing recipients and seminars.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Dependencies
- Install Python dependencies: `pip3 install -r requirements.txt` -- takes 30 seconds. NEVER CANCEL.
- Verify installation: `python3 -c "import flask, flask_sqlalchemy, flask_mail, flask_apscheduler, psycopg2, gunicorn; print('All dependencies installed')"`

### Database Setup
- **CRITICAL**: Application requires database configuration via `.env` file with `DATABASE_URL`
- Production uses PostgreSQL (connection string in `.env`)
- For local testing, modify `.env`: `DATABASE_URL=sqlite:///local_seminar.db`
- Initialize database: `python3 init_db.py` -- takes 1-2 seconds
- Seed with test data: `python3 seed_db.py` -- takes 1-2 seconds
- **NEVER** commit database files (*.db, *.sqlite) or modify the production `.env` file

### Build and Run
- **Development server**: `python3 app.py` -- starts in 2-3 seconds. Runs on http://127.0.0.1:5000
- **Production server**: `gunicorn --bind 127.0.0.1:8000 app:app` -- starts in 2-3 seconds
- **CRITICAL**: Email functionality requires Gmail SMTP configuration in `config.py`
- Application starts with APScheduler for automated email tasks
- Database tables are automatically created on startup if they don't exist

### Testing and Validation
- Syntax check: `python3 -m py_compile *.py` -- takes 1-2 seconds
- **MANUAL VALIDATION REQUIRED**: After making changes, ALWAYS test these scenarios:
  1. Access admin dashboard: `curl http://127.0.0.1:5000/admin` (should return HTML with Japanese characters)
  2. Test attendance response: `curl "http://127.0.0.1:5000/respond?seminar_id=1&recipient_id=1&status=attend"` (should return HTML)
  3. Test confirmation: `curl "http://127.0.0.1:5000/confirm?seminar_id=1&recipient_id=1"` (should return "参加確認を受け付けました。")
  4. **Browser testing**: Open http://127.0.0.1:5000/admin to test recipient/seminar management
  5. **Database verification**: Check that changes are properly stored
- Email functionality test: `python3 test_email.py` (will show "メール送信失敗: [Errno -5] No address associated with hostname" - this is expected)
- **ALWAYS** wait for Flask app to fully start (shows "Debugger PIN" message) before testing endpoints

## File Structure and Navigation

### Repository Root Files
```
├── app.py                    # Main Flask application entry point
├── models.py                 # SQLAlchemy database models  
├── routes.py                 # Flask routes and request handlers
├── config.py                 # Application configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (DATABASE_URL)
├── .gitignore               # Git ignore patterns
├── init_db.py               # Database initialization script
├── seed_db.py               # Test data seeding script
├── scheduler.py             # APScheduler tasks
├── mail_utils.py            # Email utilities
├── mailer.py                # Alternative email implementation
├── test_*.py                # Test scripts
└── templates/               # Jinja2 HTML templates
    ├── admin.html           # Admin dashboard
    ├── email_template.html  # Email invitation template
    └── confirmation_email_template.html # Confirmation email
```

### Key Navigation Points
- **Admin Interface**: Start at http://127.0.0.1:5000/admin for all management tasks
- **Database Models**: Check `models.py` for schema changes
- **Email Templates**: Modify templates in `templates/` directory for UI changes
- **Configuration**: Check `config.py` for email/database settings
- **Routes**: Check `routes.py` for URL endpoint definitions

## Key Projects and Components

### Core Application Files
- `app.py` - Main Flask application with configuration and initialization
- `models.py` - SQLAlchemy database models (Recipient, Seminar, Attendance)
- `routes.py` - URL routes and request handlers for all endpoints
- `config.py` - Application configuration including email and database settings

### Email and Scheduling
- `mail_utils.py` - Email sending utilities for invitations and confirmations
- `mailer.py` - Alternative email implementation
- `scheduler.py` - APScheduler tasks for automated email sending
- `templates/` - Jinja2 HTML templates for emails and admin interface

### Database and Setup
- `init_db.py` - Database initialization script
- `seed_db.py` - Test data seeding script
- `requirements.txt` - Python dependencies

### Test Files
- `test_email.py` - Email functionality testing
- `test_confirmation_email.py` - Confirmation email testing
- `test_email_db.py` - Database email integration testing

## Common Workflows

### Typical Development Workflow
1. Set up local database: `DATABASE_URL=sqlite:///local_seminar.db` in `.env`
2. Install dependencies: `pip3 install -r requirements.txt`
3. Initialize database: `python3 init_db.py`
4. Seed test data: `python3 seed_db.py`
5. Start development server: `python3 app.py`
6. Test admin interface at http://127.0.0.1:5000/admin
7. **ALWAYS** run manual validation scenarios after changes

### Email System Workflow
1. Admin creates seminars and recipients via web interface
2. System automatically sends invitation emails based on scheduler
3. Recipients respond via email links (attend/absent/pending/confirmed)
4. System tracks responses in Attendance table
5. Confirmation emails sent to attendees before seminar start

### Database Schema
- **Recipient**: id, name, email (unique), affiliation, phone
- **Seminar**: id, title, date, venue, speaker, topic, contact  
- **Attendance**: id, recipient_id (FK), seminar_id (FK), status

## Critical Timing and Timeouts

### Build Times and Commands
- `pip3 install -r requirements.txt` -- 30 seconds. Set timeout to 60 seconds. NEVER CANCEL.
- `python3 app.py` -- 2-3 seconds startup. Set timeout to 10 seconds. Look for "Debugger PIN" message to confirm ready.
- `gunicorn --bind 127.0.0.1:8000 app:app` -- 2-3 seconds startup. Set timeout to 10 seconds. Look for "Booting worker" message.
- Database operations (`init_db.py`, `seed_db.py`) -- 1-2 seconds each. Set timeout to 10 seconds.

### Validation Requirements
- **NEVER** skip manual validation testing after making changes
- **ALWAYS** test at least the admin dashboard and one response scenario
- Application serves Japanese language content - ensure UTF-8 encoding is maintained
- Email testing will fail without proper SMTP configuration (this is expected in development)

## Troubleshooting

### Common Issues and Solutions
- **Database connection errors**: Check `.env` file and `DATABASE_URL` setting
- **Import errors**: Run `pip3 install -r requirements.txt` to install dependencies  
- **Email sending failures**: Expected in development without SMTP configuration (shows "[Errno -5] No address associated with hostname")
- **Port conflicts**: Application runs on port 5000 by default, gunicorn uses 8000
- **Database already exists errors**: Use `rm -f *.db` to clean SQLite databases
- **Flask app not responding**: Wait for "Debugger PIN" message before testing endpoints
- **Japanese text encoding issues**: Ensure all files are saved with UTF-8 encoding

### File Locations
- Main application entry: `/app.py`
- Database models: `/models.py` 
- Admin interface templates: `/templates/admin.html`
- Email templates: `/templates/email_template.html`, `/templates/confirmation_email_template.html`
- Configuration: `/config.py` and `/.env`

### Database Management
- Production database is PostgreSQL hosted on Render
- Local development can use SQLite for testing
- **NEVER** modify production database connection strings
- Always use `init_db.py` to create tables
- Use `seed_db.py` for test data (checks for existing data)

### Email Configuration
- Uses Gmail SMTP (smtp.gmail.com:587)
- Requires app password in `config.py`
- Test scripts will fail without proper configuration (expected behavior)
- Templates support Japanese language content

## Security Notes
- Email credentials are stored in `config.py` (should be moved to environment variables)
- Database connection string contains credentials in `.env`
- No authentication required for admin interface (development only)
- Email functionality requires external SMTP service