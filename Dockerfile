# Use the official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing .pyc files to disk and prevent buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (curl might be needed for healthchecks or other network diagnostics later)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (astral-sh/uv) directly from their official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies using uv (blazing fast compared to standard pip)
RUN uv pip install --system --no-cache -r requirements.txt


# Copy the rest of the application code
COPY . .

# Expose the specific port the application will run on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
