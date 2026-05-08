# PatchGuard Manager

## Project description

PatchGuard Manager is a professional local Django web application created for coursework demonstration. It shows how patch management protects digital infrastructure from outdated software, missing security updates, misconfigurations, and cyber risks.

## Coursework topic

**Role of Patch Management in Digital Infrastructure Security**

## Technologies used

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- ReportLab for local PDF report generation

## Demo login

This is only for local coursework demonstration.

- Username: `admin`
- Password: `admin12345`

The demo user is created automatically when the login page is opened after database migration. Passwords are not stored in plain text; Django stores hashed passwords.

## Installation steps

Open the project folder in terminal:

```bash
cd patchguard_manager
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

Optional: create your own superuser:

```bash
python manage.py createsuperuser
```

Optional: create demo assets manually from terminal:

```bash
python manage.py shell -c "from core.utils import create_demo_data; create_demo_data()"
```

## How to run locally

```bash
python manage.py runserver
```

Open in browser:

```text
http://127.0.0.1:8000
```

## How to open through local network

Run the server on all local interfaces:

```bash
python manage.py runserver 0.0.0.0:8000
```

Find your computer IP address on Windows:

```bash
ipconfig
```

Open from another device connected to the same Wi-Fi network:

```text
http://LOCAL_IP_ADDRESS:8000
```

Example:

```text
http://192.168.1.10:8000
```

If Windows Firewall asks for permission, click **Allow Access**. The laptop and the second device must be connected to the same Wi-Fi network.

## Main features

- Login page with Django authentication
- Three interface languages: English, Russian, Turkmen
- Language switcher with saved language preference
- Dark and light theme support
- Dashboard with cybersecurity statistics
- Asset inventory with add, edit, delete
- Patch assessment engine
- Risk score calculation from 0 to 100
- Patch compliance percentage
- Patch priority system
- Professional report generation
- PDF report download
- Local SQLite history of previous assessments
- Educational page with academic explanations
- Responsive design for laptop and mobile screens

## Ethical and academic purpose

This application is an educational simulator. It does not scan real networks, exploit vulnerabilities, or perform offensive cybersecurity actions. It is designed to demonstrate the importance of patch management in digital infrastructure security.

## Future improvements

- Real vulnerability database integration
- CVE lookup support
- Role-based access control
- Automatic asset discovery
- Email notifications
- Advanced charts
- Export to Excel
- Integration with enterprise patch management tools
