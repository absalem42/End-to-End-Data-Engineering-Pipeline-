import requests
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherAPIBackup:
    """
    Backup weather data source using OpenWeatherMap API
    
    This class provides current weather data as a backup/supplement
    to the Wikipedia scraping approach.
    """
    
    def __init__(self, api_key):
        """
        Initialize with OpenWeatherMap API key
        
        Args:
            api_key (str): OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.uae_cities_coords = {
            'Abu Dhabi': (24.2992, 54.6969),
            'Dubai': (25.2048, 55.2708),
            'Sharjah': (25.3373, 55.4120),
            'Ajman': (25.4052, 55.5136),
            'Ras Al Khaimah': (25.7889, 55.9598),
            'Fujairah': (25.1164, 56.3265),
            'Umm Al Quwain': (25.5641, 55.6552)
        }
    
    def get_current_weather(self, city_name):
        """
        Get current weather data from OpenWeatherMap API
        
        Args:
            city_name (str): Name of the UAE city
            
        Returns:
            dict: Weather data from API or None if failed
        """
        if city_name not in self.uae_cities_coords:
            logger.error(f"City {city_name} not found in UAE cities list")
            return None
            
        lat, lon = self.uae_cities_coords[city_name]
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully retrieved API data for {city_name}")
            
            return {
                'city_name': city_name,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather_condition': data['weather'][0]['description'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'visibility': data.get('visibility', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {city_name}: {e}")
            return None
        except KeyError as e:
            logger.error(f"API response parsing error for {city_name}: {e}")
            return None
    
    def save_api_data_to_db(self, weather_data):
        """
        Save API weather data to database
        
        Args:
            weather_data (dict): Weather data from API
        """
        try:
            conn = sqlite3.connect('uae_weather.db')
            cursor = conn.cursor()
            
            # Create API data table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS current_weather_api (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    pressure REAL,
                    weather_condition TEXT,
                    wind_speed REAL,
                    visibility REAL,
                    data_source TEXT DEFAULT 'OpenWeatherMap',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO current_weather_api 
                (city_name, temperature, humidity, pressure, weather_condition, 
                 wind_speed, visibility, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_data['city_name'],
                weather_data['temperature'],
                weather_data['humidity'],
                weather_data['pressure'],
                weather_data['weather_condition'],
                weather_data['wind_speed'],
                weather_data['visibility'],
                'OpenWeatherMap'
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"API data saved for {weather_data['city_name']}")
            
        except Exception as e:
            logger.error(f"Database save error for API data: {e}")
    
    def collect_all_current_weather(self):
        """
        Collect current weather data for all UAE cities
        
        Returns:
            int: Number of cities successfully processed
        """
        success_count = 0
        
        for city_name in self.uae_cities_coords.keys():
            weather_data = self.get_current_weather(city_name)
            
            if weather_data:
                self.save_api_data_to_db(weather_data)
                success_count += 1
                print(f"✅ API data collected for {city_name}")
            else:
                print(f"❌ Failed to collect API data for {city_name}")
        
        logger.info(f"API collection completed: {success_count}/{len(self.uae_cities_coords)} cities")
        return success_count

# Example usage
if __name__ == "__main__":
    # You need to get a free API key from https://openweathermap.org/api
    API_KEY = "your_openweathermap_api_key_here"
    
    if API_KEY != "your_openweathermap_api_key_here":
        backup_api = WeatherAPIBackup(API_KEY)
        backup_api.collect_all_current_weather()
    else:
        print("Please set your OpenWeatherMap API key in the script")
        print("Get a free API key from: https://openweathermap.org/api")