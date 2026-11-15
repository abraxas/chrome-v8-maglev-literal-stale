FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        unzip \
        openssl \
        sqlite3 \
        procps \
        fontconfig \
        fonts-liberation \
        fonts-dejavu-core \
        fonts-noto-core \
        tesseract-ocr \
        scrot \
        xdotool \
        x11-utils \
        xvfb \
        openbox \
        dbus \
        dbus-x11 \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libcairo2 \
        libgtk-3-0 \
        libatspi2.0-0 \
        libxshmfence1 \
        libxss1 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxext6 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache

RUN pip install --no-cache-dir playwright==1.49.1 pillow==11.0.0

ARG VULN=157.0.8103.50
ARG FIXED=157.0.8103.78

RUN mkdir -p /opt/chrome \
    && curl -fsSL -o /tmp/chrome-vuln.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${VULN}/linux-arm64/chrome-linux-arm64.zip" \
    && unzip -q /tmp/chrome-vuln.zip -d "/opt/chrome/${VULN}" \
    && curl -fsSL -o /tmp/chrome-fixed.zip \
        "https://storage.googleapis.com/chrome-for-testing-public/${FIXED}/linux-arm64/chrome-linux-arm64.zip" \
    && unzip -q /tmp/chrome-fixed.zip -d "/opt/chrome/${FIXED}" \
    && rm -f /tmp/chrome-vuln.zip /tmp/chrome-fixed.zip \
    && "/opt/chrome/${VULN}/chrome-linux-arm64/chrome" --version --no-sandbox \
    && "/opt/chrome/${FIXED}/chrome-linux-arm64/chrome" --version --no-sandbox

LABEL lab="CVE-2026-126910"
LABEL cve="CVE-2026-126910"

WORKDIR /lab
COPY poc.py poc.html start.sh /lab/
RUN chmod +x /lab/start.sh /lab/poc.py

EXPOSE 18630
CMD ["/lab/start.sh"]
