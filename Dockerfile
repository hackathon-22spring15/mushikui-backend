FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app"]
