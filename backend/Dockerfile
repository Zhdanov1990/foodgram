FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
