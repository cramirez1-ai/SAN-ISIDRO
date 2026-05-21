# Brgy San Isidro Information Management System

Brgy San Isidro Surigao City, Surigao del Norte, Philippines Information Management System.

## Local setup

```powershell
.\run.ps1
```

Open `http://127.0.0.1:8005/`.

If PowerShell blocks the script, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

The script creates `.venv`, installs dependencies, runs migrations, and starts the development server. It requires Python 3.13 or newer to be installed and available on PATH.

Default admin:

- Username: `admin`
- Password: `Admin@12345`

## Vercel deployment

Use this folder, `barangay_system`, as the Vercel project root directory.

Vercel uses:

- `vercel.json` for routing
- `api/index.py` as the Python serverless entrypoint
- `requirements.txt` for Python dependencies

Environment variables:

- `DEBUG=False`
- `SECRET_KEY=<generate a secure value>`
- `ALLOWED_HOSTS=.vercel.app,your-app-name.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://your-app-name.vercel.app`
- `DATABASE_URL=<hosted PostgreSQL connection string>`

Use a hosted PostgreSQL database for production, such as Vercel Postgres, Neon, or Supabase. SQLite is only suitable for local development.

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
