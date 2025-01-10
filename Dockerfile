FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libglib2.0-0 \
    libglib2.0-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    shared-mime-info \
    poppler-utils \
    gobject-introspection \
    gir1.2-pango-1.0 \
    gir1.2-gdkpixbuf-2.0 \
    gtk+-3.0 \
    libgtk-3-dev \
    python3-dev \
    pkg-config \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

# Run the application
CMD ["python", "app.py"]
