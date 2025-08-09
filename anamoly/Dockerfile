# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python application script and configuration file into the container
COPY app.py .
COPY config.yaml .

# Expose the port the app will run on (if necessary)
EXPOSE 8080

# Command to run the Python application
CMD ["python", "app.py"]

