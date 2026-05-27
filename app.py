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
        "layout": "cards",
        "background": "#f5f7fb",
        "surface": "#ffffff",
        "surface_alt": "#eef2f8",
        "text": "#162033",
        "muted": "#60708a",
        "accent": "#335cff",
        "accent_2": "#00a3b5",
        "accent_soft": "#dce6ff",
        "border": "#cfdaea",
        "shadow": "rgba(30, 49, 85, 0.16)",
    },
    "1": {
        "name": "Sky Cards",
        "layout": "cards",
        "background": "#eaf7ff",
        "surface": "#ffffff",
        "surface_alt": "#d9f0ff",
        "text": "#0b2545",
        "muted": "#4d6884",
        "accent": "#0077ff",
        "accent_2": "#00b4d8",
        "accent_soft": "#c8edff",
        "border": "#9fd8ff",
        "shadow": "rgba(0, 119, 255, 0.22)",
    },
    "2": {
        "name": "Crimson Console",
        "layout": "table",
        "background": "#16070b",
        "surface": "#241014",
        "surface_alt": "#35131a",
        "text": "#fff1f2",
        "muted": "#f4a7ae",
        "accent": "#ff334e",
        "accent_2": "#ff8a00",
        "accent_soft": "#4a1620",
        "border": "#7f1d2d",
        "shadow": "rgba(255, 51, 78, 0.26)",
    },
    "3": {
        "name": "Lime Signal",
        "layout": "list",
        "background": "#dcff3f",
        "surface": "#f8ffe6",
        "surface_alt": "#12220d",
        "text": "#10230b",
        "muted": "#38512f",
        "accent": "#00a82d",
        "accent_2": "#101f0b",
        "accent_soft": "#baff7a",
        "border": "#53c926",
        "shadow": "rgba(16, 35, 11, 0.24)",
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
      --surface-alt: {{ theme.surface_alt }};
      --text: {{ theme.text }};
      --muted: {{ theme.muted }};
      --accent: {{ theme.accent }};
      --accent-2: {{ theme.accent_2 }};
      --accent-soft: {{ theme.accent_soft }};
      --border: {{ theme.border }};
      --shadow: {{ theme.shadow }};
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background: var(--background);
    }

    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 56px 0;
    }

    body.theme-1 {
      background:
        linear-gradient(120deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0) 42%),
        repeating-linear-gradient(135deg, rgba(0, 119, 255, 0.08) 0 2px, transparent 2px 18px),
        var(--background);
    }

    body.theme-2 {
      background:
        linear-gradient(90deg, rgba(255, 51, 78, 0.2), transparent 38%),
        repeating-linear-gradient(0deg, rgba(255, 138, 0, 0.08) 0 1px, transparent 1px 34px),
        var(--background);
    }

    body.theme-3 {
      background:
        linear-gradient(155deg, rgba(255, 255, 255, 0.5), transparent 30%),
        repeating-linear-gradient(90deg, rgba(16, 35, 11, 0.1) 0 1px, transparent 1px 28px),
        var(--background);
    }

    .app-shell {
      position: relative;
    }

    .app-shell::before,
    .app-shell::after {
      content: "";
      position: fixed;
      pointer-events: none;
      z-index: -1;
    }

    .app-shell::before {
      top: 24px;
      right: 28px;
      width: min(30vw, 280px);
      height: 10px;
      background: var(--accent);
      box-shadow: 0 20px 0 var(--accent-2), 0 40px 0 var(--accent-soft);
    }

    .app-shell::after {
      bottom: 24px;
      left: 28px;
      width: 180px;
      height: 180px;
      border: 1px solid var(--border);
      transform: rotate(12deg);
      opacity: 0.45;
    }

    .theme-2 .app-shell::after {
      border-width: 2px;
      box-shadow: inset 0 0 0 18px rgba(255, 51, 78, 0.08);
    }

    .theme-3 .app-shell::after {
      width: 220px;
      height: 90px;
      border-color: var(--accent-2);
      transform: skewX(-15deg);
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
    .detail-card,
    .metric-card,
    .data-table-wrap,
    .signal-list {
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: 0 24px 70px var(--shadow);
    }

    .intro {
      min-height: 360px;
      padding: 42px;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .theme-1 .intro {
      border-left: 9px solid var(--accent);
      box-shadow: 16px 16px 0 var(--accent-soft), 0 24px 70px var(--shadow);
    }

    .theme-2 .intro {
      min-height: 300px;
      background: linear-gradient(135deg, var(--surface), #110508);
      border: 1px solid var(--accent);
      box-shadow: 0 0 0 1px rgba(255, 51, 78, 0.35), 0 26px 80px var(--shadow);
    }

    .theme-3 .intro {
      min-height: 300px;
      background: var(--surface);
      border: 3px solid var(--accent-2);
      box-shadow: 12px 12px 0 var(--accent-2), 0 24px 70px var(--shadow);
    }

    .eyebrow {
      display: inline-flex;
      width: fit-content;
      padding: 7px 11px;
      border-radius: 8px;
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

    .theme-2 h1 {
      color: #ffffff;
      text-shadow: 0 0 28px rgba(255, 51, 78, 0.34);
    }

    .theme-3 h1 {
      text-transform: uppercase;
      text-shadow: 4px 4px 0 var(--accent-soft);
    }

    .lead {
      max-width: 640px;
      margin: 0;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.7;
    }

    .theme-2 .lead,
    .theme-2 .label,
    .theme-2 .row dt {
      color: var(--muted);
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
      background: var(--surface-alt);
      box-shadow: inset 0 -3px 0 var(--accent);
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

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin: 28px 0;
    }

    .metric-card {
      min-width: 0;
      padding: 20px;
      border-radius: 8px;
      position: relative;
      overflow: hidden;
    }

    .metric-card::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 6px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }

    .metric-icon,
    .list-icon {
      display: inline-grid;
      place-items: center;
      width: 38px;
      height: 38px;
      margin-bottom: 14px;
      border-radius: 8px;
      color: #ffffff;
      background: var(--accent);
      font-size: 12px;
      font-weight: 800;
      box-shadow: 0 10px 24px var(--shadow);
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

    .table-layout {
      display: grid;
      grid-template-columns: minmax(280px, 0.82fr) minmax(0, 1.18fr);
      gap: 28px;
      align-items: start;
    }

    .data-table-wrap {
      border-radius: 8px;
      overflow: hidden;
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 14px;
    }

    .data-table caption {
      padding: 22px 24px;
      color: #ffffff;
      background: linear-gradient(90deg, var(--accent), var(--surface-alt));
      font-size: 20px;
      font-weight: 800;
      text-align: left;
    }

    .data-table th,
    .data-table td {
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
      overflow-wrap: anywhere;
    }

    .data-table th {
      width: 28%;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
      background: rgba(255, 255, 255, 0.03);
    }

    .data-table td.group {
      width: 18%;
      color: var(--accent);
      font-weight: 800;
    }

    .terminal-strip {
      display: grid;
      grid-template-columns: repeat(3, 10px);
      gap: 8px;
      margin-bottom: 26px;
    }

    .terminal-strip span {
      width: 10px;
      height: 10px;
      border-radius: 2px;
      background: var(--accent);
      box-shadow: 18px 0 0 var(--accent-2);
    }

    .list-layout {
      display: grid;
      grid-template-columns: minmax(280px, 0.72fr) minmax(0, 1.28fr);
      gap: 30px;
      align-items: start;
    }

    .signal-list {
      border-radius: 8px;
      padding: 12px;
      background: var(--surface-alt);
      border: 3px solid var(--accent-2);
    }

    .signal-item {
      display: grid;
      grid-template-columns: 54px minmax(0, 1fr);
      gap: 16px;
      padding: 18px;
      border-bottom: 1px solid rgba(248, 255, 230, 0.18);
      color: #f8ffe6;
    }

    .signal-item:last-child {
      border-bottom: 0;
    }

    .signal-item .label,
    .signal-item .value {
      color: #f8ffe6;
    }

    .signal-item .label {
      margin-bottom: 4px;
      opacity: 0.78;
    }

    .signal-item .list-icon {
      margin: 0;
      color: var(--accent-2);
      background: var(--accent-soft);
      box-shadow: none;
    }

    @media (max-width: 860px) {
      main {
        width: min(100% - 24px, 720px);
        padding: 24px 0;
      }

      .hero,
      .details,
      .table-layout,
      .list-layout {
        grid-template-columns: 1fr;
      }

      .intro {
        min-height: auto;
        padding: 28px;
      }

      .quick-facts,
      .metric-grid {
        grid-template-columns: 1fr;
      }

      .row {
        grid-template-columns: 1fr;
        gap: 6px;
      }
    }
  </style>
</head>
<body class="theme-{{ theme_key }}">
  <main class="app-shell">
    {% if layout == "table" %}
    <section class="table-layout">
      <div class="intro">
        <div>
          <div class="terminal-strip"><span></span></div>
          <span class="eyebrow">Container Runtime Console</span>
          <h1>{{ app_title }}</h1>
          <p class="lead">A dark operational view for checking request and deployment values inside a running container.</p>
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

      <div class="data-table-wrap">
        <table class="data-table">
          <caption>Runtime Data</caption>
          <tbody>
            {% for item in all_items %}
            <tr>
              <td class="group">{{ item.group }}</td>
              <th scope="row">{{ item.label }}</th>
              <td>{{ item.value }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>
    {% elif layout == "list" %}
    <section class="list-layout">
      <div class="intro">
        <div>
          <span class="eyebrow">Live Container Signal</span>
          <h1>{{ app_title }}</h1>
          <p class="lead">A high-contrast status board with compact request facts and deployment values.</p>
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

      <div class="signal-list">
        {% for item in all_items %}
        <div class="signal-item">
          <span class="list-icon">{{ item.icon }}</span>
          <div>
            <div class="label">{{ item.group }} / {{ item.label }}</div>
            <div class="value">{{ item.value }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </section>
    {% else %}
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

    <section class="metric-grid">
      {% for item in summary %}
      <div class="metric-card">
        <span class="metric-icon">{{ item.icon }}</span>
        <div class="label">{{ item.label }}</div>
        <div class="value">{{ item.value }}</div>
      </div>
      {% endfor %}
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
    {% endif %}
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
        {
            "group": "Summary",
            "icon": "DNS",
            "label": "Domain",
            "value": safe_info["domain"],
        },
        {
            "group": "Summary",
            "icon": "ENV",
            "label": "APP_TITLE",
            "value": safe_info["app_title"],
        },
        {
            "group": "Summary",
            "icon": "THM",
            "label": "APP_THEME",
            "value": safe_info["app_theme"],
        },
        {
            "group": "Summary",
            "icon": "UTC",
            "label": "Request Time",
            "value": safe_info["requested_at"],
        },
    ]
    browser = [
        {
            "group": "Browser",
            "icon": "UA",
            "label": "User Agent",
            "value": safe_info["user_agent"],
        },
        {
            "group": "Browser",
            "icon": "ACC",
            "label": "Accept",
            "value": safe_info["accept"],
        },
        {
            "group": "Browser",
            "icon": "LAN",
            "label": "Language",
            "value": safe_info["accept_language"],
        },
        {
            "group": "Browser",
            "icon": "IP",
            "label": "Remote IP",
            "value": safe_info["remote_addr"],
        },
    ]
    deployment = [
        {
            "group": "Deploy",
            "icon": "CLR",
            "label": "Theme",
            "value": safe_info["theme_name"],
        },
        {
            "group": "Deploy",
            "icon": "GET",
            "label": "Method",
            "value": safe_info["method"],
        },
        {
            "group": "Deploy",
            "icon": "URL",
            "label": "Path",
            "value": safe_info["path"],
        },
        {
            "group": "Deploy",
            "icon": "TLS",
            "label": "Scheme",
            "value": safe_info["scheme"],
        },
    ]
    all_items = [*summary, *browser, *deployment]

    return app.jinja_env.from_string(HTML_TEMPLATE).render(
        app_title=safe_info["app_title"],
        domain=safe_info["domain"],
        requested_at=safe_info["requested_at"],
        theme=theme,
        theme_key=safe_info["theme_key"],
        layout=theme["layout"],
        theme_name=safe_info["theme_name"],
        summary=summary,
        browser=browser,
        deployment=deployment,
        all_items=all_items,
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
