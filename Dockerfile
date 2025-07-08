# Use official Selenium Firefox image
FROM selenium/standalone-firefox:latest

USER root

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user (optional, but safe)
RUN useradd -m manav

# Switch to user
USER manav

# Set working directory
WORKDIR /home/manav/app

# Copy your application code
COPY --chown=manav:manav . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Flask app port
EXPOSE 5000

# Run with Waitress (production WSGI server)
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "5000", "app:app"]
