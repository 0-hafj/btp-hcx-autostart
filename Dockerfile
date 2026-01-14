# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy script
COPY hana_autostart.py .

# Install dependencies
RUN pip install --no-cache-dir requests

# Set default command
ENTRYPOINT ["python", "hana_autostart.py"]