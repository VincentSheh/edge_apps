# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8001 available to the world outside this container
EXPOSE 8010

# Run the server.py script when the container launches
CMD ["python", "serve_https.py"]

