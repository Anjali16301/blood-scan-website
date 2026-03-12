FROM python:3.10-slim

WORKDIR /app

RUN apt-get update --fix-missing && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads

EXPOSE 10000

CMD ["gunicorn", "app:app", "--timeout", "120", "--workers", "1", "--bind", "0.0.0.0:10000"]
