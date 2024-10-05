# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port that the Flask app runs on
EXPOSE 5100

# Command to run the Flask application using gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5100", "app:app", "--workers=4"]

