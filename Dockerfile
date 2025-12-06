# Use official Python image
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Poetry
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# Copy dependency files first (for caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi  --no-root

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
