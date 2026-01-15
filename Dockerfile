# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize DB (in a real prod setup, this would be a separate migration step)
RUN python database.py

# Expose port
EXPOSE 8000

# Run the API server
CMD ["python", "api.py"]
