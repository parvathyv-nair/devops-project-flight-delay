FROM python:3.9-slim
WORKDIR /app

# Upgrade pip first
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
