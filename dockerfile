# Base Image
FROM python:3.12 AS base

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove the requirements file
RUN rm requirements.txt

# Update and install additional requirements
RUN apt update && apt upgrade -y && apt install git -y && rm -rf /var/lib/apt/lists/*

# Use a non-root user
RUN useradd -m appuser

# Copy the application code and change ownership
COPY --chown=appuser:appuser . .

# Expose the port
EXPOSE 8080

USER appuser

# Command to run the application
CMD ["uvicorn", "product_pipeline:app", "--host", "0.0.0.0", "--port", "8080"]