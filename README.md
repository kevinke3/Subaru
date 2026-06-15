# ClassMate

A modern, premium school management platform built with Flask, SQLAlchemy, Chart.js, and Font Awesome.

## Tech Stack
- **Backend**: Flask (Python), Flask-SQLAlchemy, Flask-JWT-Extended, Flask-SocketIO
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Fonts**: Outfit (Google Fonts)
- **Icons**: Font Awesome 6
- **Charts**: Chart.js
- **Architecture**: Flask Blueprints, role-based access control

## Quick Start
```bash
pip install -r requirements.txt
python -m app
```

Then open http://localhost:5000

## Default Credentials
Use the Register page to create accounts. Select a role (Admin, Teacher, Student, Parent) and sign in.

## Project Structure
```
app/                  # Backend package
  __init__.py         # App factory, blueprint registration
  models.py           # Core models (User, Role, Permission, Student, Teacher)
  academics/          # Classes, Subjects, Timetable, Enrollments
  attendance/         # Sessions, Records, Summaries, Leave Requests
  exams/              # Exams, Results, Report Cards, Transcripts
  finance/            # Invoices, Payments, Transactions, Fee Structures
  messaging/          # Conversations, Messages, Announcements
  analytics/          # Metrics, Activity Logs, School Stats
  notifications/      # Notification preferences
  settings/           # Profile and preferences API
  storage/            # File upload/download
  auth/               # Register, Login, Me
  admin/              # User management, audit logs
  students/           # Student CRUD
  teachers/           # Teacher CRUD

templates/            # Frontend pages
  index.html          # Marketing landing page
  login.html          # Authentication
  register.html       # Registration
  base.html           # Shared CSS/JS includes
  app-layout.html     # Sidebar + topbar layout
  dashboard.html      # Admin/Manager dashboard
  students.html       # Student management
  teachers.html       # Teacher management
  academics.html      # Classes, timetable, subjects
  attendance.html     # Attendance tracking
  finance.html        # Invoicing, payments, transactions
  exams.html          # Exams, results, report cards
  messages.html       # Messaging + announcements
  settings.html       # Profile + notification prefs
  administration.html # School overview + operations
  student-portal.html # Student self-service
  teacher-portal.html # Teacher workspace
  parent-portal.html  # Parent monitoring

static/
  css/main.css        # Design system (Outfit, glassmorphism, shadows)
  js/app.js           # API client, sidebar, dropdowns, counters, modals
```

## Environment Variables
```
DATABASE_URL=postgresql://user:pass@host/dbname
SECRET_KEY=your-secret
JWT_SECRET_KEY=your-jwt-secret
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=
```

## License
MIT
