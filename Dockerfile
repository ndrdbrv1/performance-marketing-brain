FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    psycopg2-binary \
    sqlalchemy

# Copy the rest of the application
COPY . .

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "src/run.py"]