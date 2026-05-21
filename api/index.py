import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barangay_system.settings")

try:
    from django.core.wsgi import get_wsgi_application

    app = get_wsgi_application()
except Exception as exc:
    def app(environ, start_response):
        body = f"Application failed to start: {type(exc).__name__}: {exc}".encode()
        start_response(
            "500 Internal Server Error",
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", str(len(body))),
            ],
        )
        return [body]
