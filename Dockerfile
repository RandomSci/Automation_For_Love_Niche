FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p outputs Audio_Voice

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]