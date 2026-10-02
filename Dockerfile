FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY _scripts/ ./_scripts/
COPY _schemas/ ./_schemas/
COPY _templates/ ./_templates/
COPY _index/ ./_index/
COPY birds/ ./birds/
COPY translations/ ./translations/

EXPOSE 8000

CMD ["uvicorn", "_scripts.api:app", "--host", "0.0.0.0", "--port", "8000"]