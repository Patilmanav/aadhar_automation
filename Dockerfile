# Use official Selenium Firefox image
FROM selenium/standalone-firefox:latest

# Switch to root to install Python
USER root

RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy files as non-root user
COPY --chown=seluser:seluser . /home/seluser/app

# Set working dir
WORKDIR /home/seluser/app

# Install dependencies as root globally
RUN pip3 install --no-cache-dir -r requirements.txt

# Revert to non-root user (seluser is default for selenium images)
USER seluser

EXPOSE 5000

CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "5000", "app:app"]
