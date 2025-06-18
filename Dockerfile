# Use an official Python runtime as the base image
FROM python:3.12-slim-bullseye

# Update system packages to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED 1 

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Command to run the bot (APScheduler)
CMD ["python", "src/main.py"]