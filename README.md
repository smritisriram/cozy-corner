# Cozy Corner — Keep Calm & Cozy On

A supportive student platform built with Python Django.

## Features

- **Study Courses** — Topic-based learning (Math, History, Science, Reading & Writing)
- **Practice Exams** — Timed exam simulation with countdown
- **Habit Tracker** — Custom habits, color coding, streak tracking, calendar
- **Cozy Journal** — Creative journaling with text, stickers, mood elements
- **Dumpling Chat** — Supportive AI-style chat assistant
- **Account** — Sign up without email; theme customization; progress stats

## Setup

```bash
cd cozy-corner
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000

## Sign Up

Create an account with name, password, and optional birthday/age/gender. No email required. Your username is auto-generated — find it on the Account page for future logins.

## Tech Stack

- Django 5+
- SQLite (default)
- Plain HTML/CSS/JS (no frontend framework)
