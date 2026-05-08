# Deploy PatchGuard Manager on Railway

This version is prepared for Railway deployment.

## Required Railway variables

Add these variables in Railway > Project > Service > Variables:

```text
DEBUG=False
ALLOWED_HOSTS=*
SECRET_KEY=replace-this-with-a-long-random-secret-key
```

Optional if you mount a Railway Volume for persistent SQLite storage:

```text
SQLITE_PATH=/app/data/db.sqlite3
```

## Railway start command

The project already includes `railway.json` with this start command:

```bash
python manage.py migrate --noinput && gunicorn patchguard_manager.wsgi:application --bind 0.0.0.0:$PORT
```

## Local run still works

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Demo credentials

```text
Username: admin
Password: admin12345
```

The demo user is created automatically when the login page is opened after migrations are applied.
