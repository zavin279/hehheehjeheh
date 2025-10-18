# 1. Use a standard Python image
FROM python:3.11

# 2. Set environment variables for non-interactive commands
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Install system dependencies required by psycopg2
# We need 'gcc' for compiling and 'libpq-dev' for PostgreSQL headers
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 4. Set the working directory
WORKDIR /app

# 5. Copy and install dependencies first (for efficient layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . /app/

# 7. Create the 'uploads' directory which is used in main.py
RUN mkdir -p /app/uploads

# 8. Expose the port used by uvicorn
EXPOSE 8000

# 9. Define the command to run your FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]