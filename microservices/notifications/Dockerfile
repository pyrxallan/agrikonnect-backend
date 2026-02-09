FROM python:3.11-slim

WORKDIR /service

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app/ .

# Set Python path so imports work correctly
ENV PYTHONPATH=/service

EXPOSE 5000

CMD ["python", "app.py"]
