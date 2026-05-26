FROM python:3.12-slim

LABEL org.opencontainers.image.title="Demo Web App"
LABEL org.opencontainers.image.description="A simple Flask dummy web application for container deployment demos."
LABEL org.opencontainers.image.source="https://github.com/divlv/demowebapp"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        bind9-dnsutils \
        ca-certificates \
        curl \
        iproute2 \
        iptables \
        iputils-ping \
        jq \
        less \
        lsof \
        nano \
        net-tools \
        netcat-openbsd \
        nmap \
        procps \
        traceroute \
        vim-tiny \
        wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY docker-bin/ /usr/local/bin/

RUN groupadd --system app \
    && useradd --system --gid app --home /app app \
    && chmod 0755 /usr/local/bin/getsize \
        /usr/local/bin/ffind \
        /usr/local/bin/ports \
        /usr/local/bin/portsa \
        /usr/local/bin/iptl \
        /usr/local/bin/checkport \
        /usr/local/bin/myip \
    && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
