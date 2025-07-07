# Use Python slim base
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    curl \
    wget \
    unzip \
    fonts-liberation \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libgl1 \
    && apt-get clean

# Add non-root user
RUN useradd -m manav
USER manav

# Download geckodriver
RUN GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | cut -d '"' -f 4) && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz" && \
    tar -xzf geckodriver-${GECKO_VERSION}-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-${GECKO_VERSION}-linux64.tar.gz

WORKDIR /app
COPY --chown=manav:manav . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
