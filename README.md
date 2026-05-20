# Brgy San Isidro Information Management System

Brgy San Isidro Surigao City, Surigao del Norte, Philippines Information Management System.

## Local setup

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8005
```

Open `http://127.0.0.1:8005/`.

Default admin:

- Username: `admin`
- Password: `Admin@12345`

## Render deployment

Use this folder, `barangay_system`, as the Render root directory.

Build command:

```bash
bash build.sh
```

Start command:

```bash
gunicorn barangay_system.wsgi:application
```

Environment variables:

- `DEBUG=False`
- `SECRET_KEY=<generate a secure value>`
- `ALLOWED_HOSTS=.onrender.com,your-app-name.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com`
- `DATABASE_URL=<Render PostgreSQL internal connection string>`

The included `render.yaml` can also be used as a Render Blueprint.

## Local PostgreSQL option

Instead of SQLite, set these variables before running `migrate`:

```powershell
$env:POSTGRES_DB="brgy_san_isidro"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="your_password"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
python manage.py migrate
```
