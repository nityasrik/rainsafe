# fetch_weather.py
import os
import requests
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from datetime import datetime, timezone
import ssl
import json
import time

# Load environment variables from your .env file
load_dotenv()

# --- Configuration ---
MONGO_URI = os.getenv("MONGO_URI")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# List of cities in India to fetch weather data for
TARGET_CITIES = [
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
]

# --- Database Connection with Fallback ---
def connect_to_mongodb():
    """Attempt to connect to MongoDB with multiple SSL configurations and fallback options."""
    
    print("🔍 Attempting MongoDB connection...")
    print("💡 If connection fails, weather data will be saved to JSON file instead.")
    print()
    
    # Get current IP for troubleshooting
    try:
        import requests
        current_ip = requests.get('https://ipinfo.io/ip', timeout=5).text.strip()
        print(f"📋 Your current IP: {current_ip}")
        print("🔧 If connection fails, ensure this IP is whitelisted in MongoDB Atlas.")
        print()
    except:
        current_ip = "Unknown"
    
    # Configuration options to try
    connection_configs = [
        # Option 1: Standard Atlas configuration
        {
            "name": "Standard Atlas Configuration",
            "config": {
                "tls": True,
                "tlsAllowInvalidCertificates": False,
                "tlsAllowInvalidHostnames": False,
                "retryWrites": True,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000
            }
        },
        # Option 2: More permissive SSL settings
        {
            "name": "Permissive SSL Settings",
            "config": {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "tlsAllowInvalidHostnames": True,
                "retryWrites": True,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000
            }
        },
        # Option 3: Basic configuration
        {
            "name": "Basic Configuration",
            "config": {
                "retryWrites": True,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000
            }
        }
    ]
    
    for i, option in enumerate(connection_configs, 1):
        try:
            print(f"🔄 Attempting MongoDB connection (Option {i}: {option['name']})...")
            client = pymongo.MongoClient(MONGO_URI, **option["config"])
            
            # Test the connection
            client.admin.command('ping')
            
            print(f"✅ Successfully connected to MongoDB using Option {i}.")
            return client, True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Option {i} failed: SSL/TLS handshake error")
            if i == len(connection_configs):
                print("\n" + "="*60)
                print("⚠️  MONGODB CONNECTION FAILED - USING FALLBACK MODE")
                print("="*60)
                print("🔧 TROUBLESHOOTING STEPS:")
                print("1. Check MongoDB Atlas Network Access:")
                print(f"   - Add IP address: {current_ip}")
                print("   - Or add 0.0.0.0/0 for testing (less secure)")
                print()
                print("2. Check if you're behind a corporate firewall:")
                print("   - Try connecting from a different network (mobile hotspot)")
                print("   - Check if your organization blocks MongoDB connections")
                print()
                print("3. Verify MongoDB Atlas cluster status:")
                print("   - Ensure your cluster is running")
                print("   - Check if your database user has proper permissions")
                print("="*60)
                print("📁 Weather data will be saved to JSON file instead.")
                print("="*60)
                return None, False
            continue
        except Exception as e:
            print(f"❌ Unexpected error with Option {i}: {e}")
            if i == len(connection_configs):
                print("📁 Weather data will be saved to JSON file instead.")
                return None, False
            continue

# Try to connect to MongoDB
try:
    client, db_connected = connect_to_mongodb()
    if db_connected:
        db = client.rainsafe_db
        weather_collection = db.weather_data
        print("✅ MongoDB connection established successfully!")
    else:
        client = None
        db = None
        weather_collection = None
        print("⚠️  MongoDB connection failed - using fallback mode")
except Exception as e:
    print(f"❌ Could not establish MongoDB connection: {e}")
    client = None
    db = None
    weather_collection = None
    db_connected = False


# --- Fetch and Store Weather Data ---
def fetch_and_store_weather():
    """
    Fetches current weather and 5-day forecast for target cities and stores it in MongoDB or JSON file.
    """
    all_weather_data = []
    
    print(f"🌤️  Fetching weather data for {len(TARGET_CITIES)} cities...")
    print("="*60)
    
    for city in TARGET_CITIES:
        try:
            print(f"🌤️  Fetching weather data for {city['name']}...")
            
            # --- 1. Get CURRENT weather data (Standard Free API) ---
            current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
            current_response = requests.get(current_weather_url, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()

            # --- 2. Get FORECAST data (Standard Free API) ---
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={city['lat']}&lon={city['lon']}&appid={OPENWEATHER_API_KEY}&units=metric"
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # --- 3. Combine and structure the document ---
            weather_document = {
                "city_name": city["name"],
                "coordinates": { "type": "Point", "coordinates": [city["lon"], city["lat"]] },
                "current_weather": {
                    "temp": current_data['main']['temp'],
                    "humidity": current_data['main']['humidity'],
                    "weather_condition": current_data['weather'][0]['description'],
                    "rain_1h_mm": current_data.get('rain', {}).get('1h', 0),
                    "pressure": current_data['main']['pressure'],
                    "wind_speed": current_data.get('wind', {}).get('speed', 0)
                },
                "forecast_data": forecast_data['list'],  # This is a list of 3-hour forecasts
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Try to store in MongoDB if connected
            if db_connected and weather_collection is not None:
                try:
                    weather_collection.insert_one(weather_document)
                    print(f"✅ Successfully fetched and stored weather data for {city['name']} in MongoDB.")
                    # Add to summary data for display
                    all_weather_data.append(weather_document)
                except Exception as db_error:
                    print(f"⚠️  MongoDB storage failed for {city['name']}: {db_error}")
                    print(f"📁 Adding {city['name']} data to JSON fallback...")
                    all_weather_data.append(weather_document)
            else:
                # Add to JSON fallback
                all_weather_data.append(weather_document)
                print(f"✅ Successfully fetched weather data for {city['name']} (JSON fallback).")

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error fetching data for {city['name']}: {e}")
            if "401" in str(e):
                print("💡 This appears to be an API key issue. Please check your OpenWeather API key.")
        except Exception as e:
            print(f"❌ An error occurred for {city['name']}: {e}")
    
    # Save to JSON file if we have data and MongoDB is not connected
    if all_weather_data and not db_connected:
        save_to_json_file(all_weather_data)
    
    # Display summary
    display_weather_summary(all_weather_data)

def save_to_json_file(weather_data):
    """Save weather data to JSON file."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"weather_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Weather data saved to: {filename}")
        print(f"📊 Total cities processed: {len(weather_data)}")
        
    except Exception as e:
        print(f"❌ Error saving to JSON file: {e}")

def display_weather_summary(weather_data):
    """Display a summary of fetched weather data."""
    if weather_data:
        print(f"\n📋 WEATHER SUMMARY:")
        print("="*60)
        for data in weather_data:
            current = data['current_weather']
            print(f"🏙️  {data['city_name']}:")
            print(f"   🌡️  Temperature: {current['temp']}°C")
            print(f"   💧 Humidity: {current['humidity']}%")
            print(f"   🌤️  Condition: {current['weather_condition']}")
            print(f"   🌧️  Rain (1h): {current['rain_1h_mm']}mm")
            print(f"   🌬️  Wind: {current['wind_speed']} m/s")
            print()
    else:
        print("❌ No weather data was successfully fetched.")
        print("💡 Check your OpenWeather API key and internet connection.")


if __name__ == "__main__":
    print("🌤️  RAINSAFE WEATHER DATA FETCHER")
    print("="*50)
    print("💡 This script fetches weather data for major Indian cities")
    print("💡 Data is stored in MongoDB or saved to JSON file as fallback")
    print("="*50)
    
    if not OPENWEATHER_API_KEY:
        print("❌ Error: OPENWEATHER_API_KEY not found in .env file.")
        print("💡 Please get a free API key from https://openweathermap.org/api")
        print("💡 Add it to your .env file: OPENWEATHER_API_KEY=\"your_key_here\"")
        print()
        print("🔧 QUICK SETUP:")
        print("1. Go to https://openweathermap.org/api")
        print("2. Click 'Sign Up' and create a free account")
        print("3. Go to 'API keys' section")
        print("4. Copy your default API key")
        print("5. Update your .env file with: OPENWEATHER_API_KEY=\"your_actual_key\"")
        print("6. Run this script again")
        exit()
    else:
        try:
            fetch_and_store_weather()
            
            # Display final status
            print("\n" + "="*60)
            if db_connected:
                print("✅ Weather data successfully fetched and stored in MongoDB!")
            else:
                print("⚠️  Weather data fetched and saved to JSON file (MongoDB unavailable)")
                print("💡 To enable MongoDB storage:")
                print("   1. Add your IP to MongoDB Atlas Network Access")
                print("   2. Ensure your cluster is running")
                print("   3. Check your database user permissions")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n⚠️  Process interrupted by user.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            # Close the DB connection if it exists
            if client:
                try:
                    client.close()
                    print("🔒 MongoDB connection closed.")
                except:
                    pass