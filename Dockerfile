# Base image
FROM python:3.11

# Copy the current content to /app directory inside the container
COPY . /app

# Set working directory for subsequent commands
WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Add Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Add necessary packages for Python
RUN apt-get install -y python3-dev python3-pandas

# Upgrade pip and install dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files for Django
# RUN python manage.py collectstatic --no-input

# Run Django migrations
# RUN python manage.py migrate

# Install Google Chrome and curl
RUN apt-get install -y google-chrome-stable curl

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port as an environment variable
ENV DISPLAY=:99
