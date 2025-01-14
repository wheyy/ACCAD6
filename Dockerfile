# Description: Dockerfile for the flask
# Specifies the baseImage
FROM python:alpine 

# Setting the working directory
WORKDIR /app

# Copy the requirements.txt file first
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
# This acts as documentation, because the port is not actually exposed
EXPOSE 8000

CMD ["python", "app.py"]