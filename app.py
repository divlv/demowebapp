import logging
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, request
from markupsafe import escape


RUN_ID = "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}

THEMES = {
    "default": {
        "name": "Default",
        "background": "#f7f9fc",
        "surface": "#ffffff",
        "text": "#172033",
        "muted": "#5b6578",
        "accent": "#2563eb",
        "accent_soft": "#dbeafe",
        "border": "#d9e1ee",
    },
    "1": {
        "name": "Ocean",
        "background": "#eef8fb",
        "surface": "#ffffff",
        "text": "#102a43",
        "muted": "#52677a",
        "accent": "#0077b6",
        "accent_soft": "#caf0f8",
        "border": "#b6dce6",
    },
    "2": {
        "name": "Forest",
        "background": "#f2f7f0",
        "surface": "#ffffff",
        "text": "#183a2e",
        "muted": "#58685f",
        "accent": "#2f7d32",
        "accent_soft": "#dcefd8",
        "border": "#c8dec2",
    },
    "3": {
        "name": "Sunrise",
        "background": "#fff7ed",
        "surface": "#ffffff",
        "text": "#3b2416",
        "muted": "#716052",
        "accent": "#c2410c",
        "accent_soft": "#ffedd5",
        "border": "#fed7aa",
    },
}

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ app_title }}</title>
  <style>
    :root {
      --background: {{ theme.background }};
      --surface: {{ theme.surface }};
      --text: {{ theme.text }};
      --muted: {{ theme.muted }};
      --accent: {{ theme.accent }};
      --accent-soft: {{ theme.accent_soft }};
      --border: {{ theme.border }};
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.74), rgba(255, 255, 255, 0)),
        var(--background);
    }

    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 56px 0;
    }

    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
      gap: 32px;
      align-items: stretch;
      margin-bottom: 28px;
    }

    .intro,
    .panel,
    .detail-card {
      background: color-mix(in srgb, var(--surface) 92%, transparent);
      border: 1px solid var(--border);
      box-shadow: 0 20px 60px rgba(27, 39, 61, 0.08);
    }

    .intro {
      min-height: 360px;
      padding: 42px;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .eyebrow {
      display: inline-flex;
      width: fit-content;
      padding: 7px 11px;
      border-radius: 999px;
      color: var(--accent);
      background: var(--accent-soft);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0;
    }

    h1 {
      margin: 28px 0 16px;
      font-size: clamp(40px, 7vw, 72px);
      line-height: 0.95;
      letter-spacing: 0;
    }

    .lead {
      max-width: 640px;
      margin: 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.7;
    }

    .quick-facts {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 34px;
    }

    .fact {
      min-width: 0;
      padding: 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.54);
    }

    .label {
      margin-bottom: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .value {
      overflow-wrap: anywhere;
      font-size: 15px;
      font-weight: 700;
    }

    .panel {
      padding: 28px;
      border-radius: 8px;
    }

    .panel h2,
    .details h2 {
      margin: 0 0 18px;
      font-size: 20px;
      letter-spacing: 0;
    }

    .row {
      display: grid;
      grid-template-columns: 140px minmax(0, 1fr);
      gap: 16px;
      padding: 14px 0;
      border-bottom: 1px solid var(--border);
    }

    .row:last-child {
      border-bottom: 0;
    }

    .row dt {
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    .row dd {
      margin: 0;
      min-width: 0;
      overflow-wrap: anywhere;
      font-size: 14px;
      line-height: 1.55;
    }

    .details {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .detail-card {
      padding: 24px;
      border-radius: 8px;
    }

    @media (max-width: 860px) {
      main {
        width: min(100% - 24px, 720px);
        padding: 24px 0;
      }

      .hero,
      .details {
        grid-template-columns: 1fr;
      }

      .intro {
        min-height: auto;
        padding: 28px;
      }

      .quick-facts {
        grid-template-columns: 1fr;
      }

      .row {
        grid-template-columns: 1fr;
        gap: 6px;
      }
    }
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="intro">
        <div>
          <span class="eyebrow">Container Demo Application</span>
          <h1>{{ app_title }}</h1>
          <p class="lead">A lightweight Flask landing page that shows runtime details for container, ingress, and environment-variable demonstrations.</p>
        </div>
        <div class="quick-facts">
          <div class="fact">
            <div class="label">Domain</div>
            <div class="value">{{ domain }}</div>
          </div>
          <div class="fact">
            <div class="label">Theme</div>
            <div class="value">{{ theme_name }}</div>
          </div>
          <div class="fact">
            <div class="label">Requested</div>
            <div class="value">{{ requested_at }}</div>
          </div>
        </div>
      </div>

      <aside class="panel">
        <h2>Runtime Summary</h2>
        <dl>
          {% for item in summary %}
          <div class="row">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
          {% endfor %}
        </dl>
      </aside>
    </section>

    <section class="details">
      <div class="detail-card">
        <h2>Browser Request</h2>
        <dl>
          {% for item in browser %}
          <div class="row">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
          {% endfor %}
        </dl>
      </div>
      <div class="detail-card">
        <h2>Deployment Context</h2>
        <dl>
          {% for item in deployment %}
          <div class="row">
            <dt>{{ item.label }}</dt>
            <dd>{{ item.value }}</dd>
          </div>
          {% endfor %}
        </dl>
      </div>
    </section>
  </main>
</body>
</html>
"""

app = Flask(__name__)


def configure_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s RunId: %(run_id)s %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RunIdFilter())

    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RunIdFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


class RunIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = RUN_ID
        return True


configure_logging()
logger = logging.getLogger(__name__)


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        name: "<REDACTED>" if name.lower() in SENSITIVE_HEADERS else value
        for name, value in headers.items()
    }


def is_browser_request() -> bool:
    user_agent = request.headers.get("User-Agent", "").lower()
    accept = request.headers.get("Accept", "").lower()
    command_line_markers = (
        "curl",
        "wget",
        "httpie",
        "python-requests",
        "powershell",
        "invoke-webrequest",
    )

    if any(marker in user_agent for marker in command_line_markers):
        return False

    return "text/html" in accept or any(
        marker in user_agent
        for marker in ("mozilla", "chrome", "safari", "firefox", "edge", "edg/")
    )


def get_theme(theme_value: str | None) -> tuple[str, dict[str, str]]:
    if theme_value in THEMES:
        return theme_value, THEMES[theme_value]
    return "default", THEMES["default"]


def build_request_info() -> dict[str, str]:
    app_title = os.getenv("APP_TITLE") or "APP_TITLE not set"
    app_theme = os.getenv("APP_THEME") or "APP_THEME not set"
    theme_key, theme = get_theme(os.getenv("APP_THEME"))
    requested_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    return {
        "app_title": app_title,
        "app_theme": app_theme,
        "theme_key": theme_key,
        "theme_name": theme["name"],
        "domain": request.host,
        "requested_at": requested_at,
        "user_agent": request.headers.get("User-Agent", "User-Agent not set"),
        "accept": request.headers.get("Accept", "Accept not set"),
        "accept_language": request.headers.get(
            "Accept-Language", "Accept-Language not set"
        ),
        "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr or ""),
        "method": request.method,
        "path": request.full_path.rstrip("?"),
        "scheme": request.headers.get("X-Forwarded-Proto", request.scheme),
    }


def render_text(info: dict[str, str]) -> str:
    lines = [
        "Demo Web Application",
        f"Domain: {info['domain']}",
        f"APP_TITLE: {info['app_title']}",
        f"APP_THEME: {info['app_theme']}",
        f"Theme: {info['theme_name']}",
        f"Requested At: {info['requested_at']}",
        f"User Agent: {info['user_agent']}",
        f"Accept: {info['accept']}",
        f"Accept-Language: {info['accept_language']}",
        f"Remote Address: {info['remote_addr']}",
        f"Method: {info['method']}",
        f"Path: {info['path']}",
        f"Scheme: {info['scheme']}",
    ]
    return "\n".join(lines) + "\n"


def render_html(info: dict[str, str]) -> str:
    theme = THEMES[info["theme_key"]]
    safe_info = {key: escape(value) for key, value in info.items()}
    summary = [
        {"label": "Domain", "value": safe_info["domain"]},
        {"label": "APP_TITLE", "value": safe_info["app_title"]},
        {"label": "APP_THEME", "value": safe_info["app_theme"]},
        {"label": "Request Time", "value": safe_info["requested_at"]},
    ]
    browser = [
        {"label": "User Agent", "value": safe_info["user_agent"]},
        {"label": "Accept", "value": safe_info["accept"]},
        {"label": "Language", "value": safe_info["accept_language"]},
        {"label": "Remote IP", "value": safe_info["remote_addr"]},
    ]
    deployment = [
        {"label": "Theme", "value": safe_info["theme_name"]},
        {"label": "Method", "value": safe_info["method"]},
        {"label": "Path", "value": safe_info["path"]},
        {"label": "Scheme", "value": safe_info["scheme"]},
    ]

    return app.jinja_env.from_string(HTML_TEMPLATE).render(
        app_title=safe_info["app_title"],
        domain=safe_info["domain"],
        requested_at=safe_info["requested_at"],
        theme=theme,
        theme_name=safe_info["theme_name"],
        summary=summary,
        browser=browser,
        deployment=deployment,
    )


@app.get("/")
def index() -> Response:
    info = build_request_info()
    headers = redact_headers(dict(request.headers))
    body = request.get_data(as_text=True) or ""
    logger.info("Request headers: %s", headers)
    logger.info("Request query parameters: %s", dict(request.args))
    logger.info("Request body: %s", body)

    if is_browser_request():
        response = Response(render_html(info), mimetype="text/html")
    else:
        response = Response(render_text(info), mimetype="text/plain")

    logger.info("Response status: %s", response.status)
    logger.info("Response headers: %s", dict(response.headers))
    logger.info("Response body: %s", response.get_data(as_text=True))
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
