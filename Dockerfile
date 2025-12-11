# Stage 1: Build
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the image
COPY requirements.txt .

# Install Python dependencies safely
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the actual application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
