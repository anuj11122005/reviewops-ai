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
RUN pip install --no-cache-dir -e ".[dev]"

# Create a non-root user and change ownership of the application directory
RUN useradd -m -r appuser && chown -R appuser:appuser /app

COPY . .

# Switch to the non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
