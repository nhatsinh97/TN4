FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY database ./database


# Environment variables are provided via an external .env file
# passed with `docker run --env-file`. This keeps sensitive
# configuration out of the image.

EXPOSE 58888

CMD ["python", "src/app.py"]
