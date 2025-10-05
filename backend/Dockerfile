# Dockerfile

# Use the full Python image for better system library compatibility
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose port 8000 so we can access the app from outside the container
EXPOSE 8000

# Define the command to run your app when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]