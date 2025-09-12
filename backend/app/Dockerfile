# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY ../req.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the application code
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI server with auto-reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
