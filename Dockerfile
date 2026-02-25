# Dockerfile for Flask Chat App with MySQL
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install flask mysql-connector-python

EXPOSE 5000

CMD ["python", "app.py"]
