FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

EXPOSE 5001
EXPOSE 8000

CMD ["python", "main.py"]
