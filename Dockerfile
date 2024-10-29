# Use the official Python image
FROM python:3.11-slim


# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app
COPY main.py .

# Expose the port on which the app will run
EXPOSE 1070

# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "1070"]

