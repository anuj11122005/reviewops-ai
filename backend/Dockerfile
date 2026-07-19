FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and Node.js (for ESLint).
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy project files and install Python dependencies.
COPY pyproject.toml ./
RUN pip install uv && uv pip install --system --no-cache -e ".[dev]"

# Create a non-root user
RUN useradd -m -r appuser

# Copy application source with correct ownership from the start
COPY --chown=appuser:appuser . .

# Ensure the entire /app directory (including pip-installed files from earlier layers) is owned by appuser
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
