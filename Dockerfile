FROM python:3.10-slim

# Install system dependencies (ffmpeg + fonts for subtitles)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto \
    fonts-noto-extra \
    fonts-crosextra-carlito \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Fonts (Dancing Script, Great Vibes, etc.)
RUN mkdir -p /usr/share/fonts/truetype/google-fonts && \
    cd /usr/share/fonts/truetype/google-fonts && \
    wget -q https://github.com/google/fonts/raw/main/ofl/dancingscript/DancingScript%5Bwght%5D.ttf -O DancingScript.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/alexbrush/AlexBrush-Regular.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/reeniebeanie/ReenieBeanie-Regular.ttf && \
    fc-cache -f -v

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Create output directory
RUN mkdir -p outputs Audio_Voice

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI server - Railway provides $PORT variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}