FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install curl for container health checks and utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create virtualenv in /opt/venv (isolated from /app volume mount)
RUN uv venv /opt/venv

# Install dependencies using pyproject.toml
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN uv pip install --no-cache -e .

# Copy remaining project files
COPY . .

# Ensure data and logs directories and permissions
RUN mkdir -p /app/data /app/logs && chmod -R 777 /app/data /app/logs /opt/venv

EXPOSE 8050

CMD ["python", "app.py"]
