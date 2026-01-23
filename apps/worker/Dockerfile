FROM python:3.11-slim

# Install system dependencies including Playwright requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    poppler-utils \
    libmagic1 \
    curl \
    unzip \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Create data directory for local storage fallback
RUN mkdir -p /data

CMD ["sh", "-c", "rq worker --url ${REDIS_URL:-redis://localhost:6379/0} high default low"]
