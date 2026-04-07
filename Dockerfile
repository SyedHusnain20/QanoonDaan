# ── Base image ─────────────────────────────────────────────
FROM python:3.10-slim

# ── Set working directory ───────────────────────────────────
WORKDIR /app

# ── Install system dependencies ─────────────────────────────
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first (for Docker layer caching) ──────
COPY requirements.txt .

# ── Install Python dependencies ─────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy entire project ─────────────────────────────────────
COPY . .

# ── HF Spaces runs as non-root user — fix permissions ───────
RUN chmod -R 777 /app

# ── Expose port 7860 (required by HF Spaces) ────────────────
EXPOSE 7860

# ── Run the app ─────────────────────────────────────────────
CMD ["python", "app.py"]
