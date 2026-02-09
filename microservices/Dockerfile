FROM python:3.9-slim

WORKDIR /service

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Python path
ENV PYTHONPATH=/service

EXPOSE 5000

# Run the app
CMD ["python", "app/app.py"]
