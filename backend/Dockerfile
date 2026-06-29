FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy only needed files first for better layer caching
COPY requirements.txt ./
COPY main.py ./
COPY src/ ./src/
COPY config/ ./config/

# Install dependencies
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the backend port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
