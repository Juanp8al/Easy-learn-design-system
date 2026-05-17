# Local dev: SQLite + required email settings (see django_pkms/settings.py)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& ".\.venv\Scripts\Activate.ps1"
# Override if your shell still has another project (e.g. MiUniversidad) configured:
$env:DJANGO_SETTINGS_MODULE = "django_pkms.settings"
$env:DEVELOPMENT_MODE = "True"
$env:DEBUG = "True"
$env:EMAIL_HOST = "localhost"
$env:EMAIL_HOST_USER = "dev@localhost"
$env:EMAIL_HOST_PASSWORD = ""
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "False"
$env:DEFAULT_FROM_EMAIL = "dev@localhost"
python manage.py runserver @args
