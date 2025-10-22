# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps for building some Python packages (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy entrypoint and requirements first
COPY docker-entrypoint.sh requirements.txt /app/

# Set executable permissions for entrypoint
RUN chmod +x /app/docker-entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . /app/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash botuser && chown -R botuser:botuser /app
USER botuser

# Expose nothing by default (Telegram bot uses outbound connections)

# Healthcheck: ensure the process is running (simple check)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD pgrep -f main.py || exit 1

ENTRYPOINT ["bash", "/app/docker-entrypoint.sh"]
CMD ["python", "main.py"]
