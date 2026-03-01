FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy requirements
COPY backend/requirements.txt .

RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy entire project folders
COPY backend/app ./app
COPY ml ./ml
COPY data ./data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]