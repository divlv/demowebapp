# Demo Web App

A small Flask dummy web application for demonstrating container hosting platforms such as Azure Container Apps, Kubernetes, Docker, or any service that can run a container image.

The app renders a polished landing page for browser requests and returns the same runtime summary as plain text for command-line clients such as `curl` or `wget`.

## What It Shows

On every request, the application displays:

- The domain name used to call the app.
- The value of `APP_TITLE`, or `APP_TITLE not set` when the variable is missing.
- The value of `APP_THEME`, or `APP_THEME not set` when the variable is missing.
- Browser/request details such as User-Agent, Accept, Accept-Language, remote address, method, path, and scheme.
- The UTC time when the request was handled.

## Themes

For browser requests, `APP_THEME` changes the page color scheme:

- `APP_THEME=1` - Sky Cards: a light blue card-based layout.
- `APP_THEME=2` - Crimson Console: a dark red table-based layout.
- `APP_THEME=3` - Lime Signal: a bright green icon-list layout.
- Any missing or unsupported value uses the default theme.

## Run Locally with Python

Create a virtual environment, install dependencies, and start the Flask app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:APP_TITLE = "Demo Web App"
$env:APP_THEME = "1"
python app.py
```

Open:

```text
http://localhost:8000
```

Test plain-text output:

```powershell
curl http://localhost:8000
```

## Build and Run with Docker

Build the image locally:

```powershell
docker build -t demowebapp:local .
```

Run it:

```powershell
docker run --rm -p 8080:8000 -e APP_TITLE="Demo Web App" -e APP_THEME=1 demowebapp:local
```

Open:

```text
http://localhost:8080
```

## Use the GitHub Container Registry Image

The GitHub Actions pipeline publishes the image to GitHub Container Registry on every push to the `main` branch:

```text
ghcr.io/divlv/demowebapp:latest
```

Pull and run the published image:

```powershell
docker pull ghcr.io/divlv/demowebapp:latest
docker run --rm -p 8080:8000 -e APP_TITLE="Demo Web App" -e APP_THEME=1 ghcr.io/divlv/demowebapp:latest
```

Then open:

```text
http://localhost:8080
```

## GitHub Container Registry Visibility

The workflow uses the repository `GITHUB_TOKEN` to publish the image. After the first successful publish, make the package public once in GitHub:

1. Open the repository on GitHub.
2. Go to the package page for `demowebapp`.
3. Open package settings.
4. Change package visibility to Public.

After that, users can pull the image without authenticating to GitHub Container Registry.

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `APP_TITLE` | Text shown as the landing page title. | `APP_TITLE not set` |
| `APP_THEME` | Browser theme selector: `1`, `2`, or `3`. | `APP_THEME not set` |
