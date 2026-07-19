FROM python:3.12-slim

WORKDIR /ml-pipeline

# Install uv for fast pip installs
RUN pip install uv

COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Create non-root user (optional but good practice)
RUN useradd -m -r appuser
COPY --chown=appuser:appuser . .
RUN chown -R appuser:appuser /ml-pipeline
USER appuser

# Set default python path or run command
CMD ["python", "simulate_drift.py"]
