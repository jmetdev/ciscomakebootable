FROM python:3.13-slim-trixie
# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    genisoimage \
    rsync \
    isolinux \
    sudo \
    curl \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

# Create app user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories
RUN mkdir -p /app/uploads /app/output /app/templates /app/tmp

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/index.html templates/

# Create a sudoers entry for appuser to run mount/umount without password
RUN echo "appuser ALL=(ALL) NOPASSWD: /bin/mount, /bin/umount" > /etc/sudoers.d/appuser

# Set proper permissions for all directories including tmp
RUN chown -R appuser:appuser /app
RUN chmod 755 /app/uploads /app/output /app/templates
RUN chmod 777 /app/tmp

# Switch to appuser
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Default command
CMD ["python3", "app.py"]
