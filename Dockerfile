FROM python:3.12-slim

LABEL org.opencontainers.image.title="Demo Web App"
LABEL org.opencontainers.image.description="A simple Flask dummy web application for container deployment demos."
LABEL org.opencontainers.image.source="https://github.com/divlv/demowebapp"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN groupadd --system app \
    && useradd --system --gid app --home /app app \
    && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
