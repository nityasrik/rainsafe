#!/bin/bash

# Cron script for weather data fetching
# This script sets up the proper environment for cron execution

# Set the working directory
cd /home/nitya/rainsafe-backend

# Set environment variables (since cron doesn't load .env files)
export OPENWEATHER_API_KEY="b75b8b755e6dc7b20952e0fd0fb14c47"
export MONGO_URI="mongodb+srv://nityasrikanukolanu24_db_user:wT!7wkKmL3XJYGZ@cluster0.y167ax2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Activate virtual environment and run the script
source venv/bin/activate
python3 app/services/weather_service.py

# Log the execution (optional)
echo "$(date): Weather data fetch completed" >> /home/nitya/rainsafe-backend/cron.log