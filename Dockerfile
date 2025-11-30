# Use official slim Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies commonly needed for Python packages (add/remove as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libssl-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    unixodbc-dev \
    curl \
    openssh-server \
  && rm -rf /var/lib/apt/lists/*

# Ensure pip/setuptools/wheel are up-to-date before installing requirements
RUN python -m pip install --upgrade pip

# Copy and install Python requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (manage.py at repo root, all code under app/)
COPY . .

# Create app user and required directories
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/db /app/static \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Ensure settings referring to STATIC_ROOT/DB can succeed during collectstatic
ENV HOME=/home/appuser
ENV PATH="$HOME/.local/bin:$PATH"

# Collect static files at build time (will use settings configured in your project)
# If collectstatic fails during build and you want to continue, remove --noinput or
# run collectstatic at runtime instead.
RUN python manage.py collectstatic --noinput

# Expose default Django port
EXPOSE 8000
EXPOSE 2222

# Default command: run migrations then start development server.
# For production replace this with Gunicorn or another WSGI server.
CMD ["sh", "-c", "/usr/sbin/sshd -D && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]