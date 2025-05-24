import requests
from bs4 import BeautifulSoup as Bf
import sqlite3
import logging
from datetime import datetime
import time
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UAEWeatherExtractor:
    """
    UAE Weather Data Extractor
    
    Extracts weather and climate data from Wikipedia for seven UAE cities
    and stores the data in a SQLite database for analysis.
    """
    
    def __init__(self):
        self.uae_cities = {
            'Abu Dhabi': 'https://en.wikipedia.org/wiki/Abu_Dhabi',
            'Dubai': 'https://en.wikipedia.org/wiki/Dubai',
            'Sharjah': 'https://en.wikipedia.org/wiki/Sharjah',
            'Ajman': 'https://en.wikipedia.org/wiki/Ajman',
            'Ras Al Khaimah': 'https://en.wikipedia.org/wiki/Ras_Al_Khaimah',
            'Fujairah': 'https://en.wikipedia.org/wiki/Fujairah',
            'Umm Al Quwain': 'https://en.wikipedia.org/wiki/Umm_Al_Quwain'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; UAEWeatherBot/1.0; Educational purposes)'
        })
        
    def init_database(self):
        """Initialize SQLite database with weather data schema"""
        try:
            conn = sqlite3.connect('uae_weather.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    climate_type TEXT,
                    avg_temperature_celsius REAL,
                    avg_humidity_percent REAL,
                    annual_rainfall_mm REAL,
                    hottest_month TEXT,
                    coldest_month TEXT,
                    weather_description TEXT,
                    data_source TEXT DEFAULT 'Wikipedia',
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city_name, date(extracted_at))
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
            
    def extract_weather_from_wikipedia(self, city_name, url):
        """Extract weather/climate data from Wikipedia page"""
        try:
            logger.info(f"Extracting weather data for {city_name}")
            
            # Add delay to respect rate limiting
            time.sleep(2)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = Bf(response.text, 'html.parser')
            
            weather_data = {
                'city_name': city_name,
                'latitude': None,
                'longitude': None,
                'climate_type': None,
                'avg_temperature_celsius': None,
                'avg_humidity_percent': None,
                'annual_rainfall_mm': None,
                'hottest_month': None,
                'coldest_month': None,
                'weather_description': None
            }
            
            # Extract coordinates from geo microformat
            self._extract_coordinates(soup, weather_data)
            
            # Extract climate information from various sections
            self._extract_climate_info(soup, weather_data)
            
            # Extract from infobox
            self._extract_infobox_climate(soup, weather_data)
            
            # Extract from climate tables
            self._extract_climate_tables(soup, weather_data)
            
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"Network error for {city_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Extraction error for {city_name}: {e}")
            return None
    
    def _extract_coordinates(self, soup, weather_data):
        """Extract latitude and longitude coordinates"""
        try:
            # Look for geo coordinates in various formats
            geo_span = soup.find('span', class_='geo')
            if geo_span:
                coords_text = geo_span.get_text().strip()
                coords = coords_text.split(';')
                if len(coords) == 2:
                    weather_data['latitude'] = float(coords[0].strip())
                    weather_data['longitude'] = float(coords[1].strip())
                    logger.info(f"Found coordinates: {weather_data['latitude']}, {weather_data['longitude']}")
        except Exception as e:
            logger.warning(f"Could not extract coordinates: {e}")
    
    def _extract_climate_info(self, soup, weather_data):
        """Extract climate information from text content"""
        try:
            # Look for climate section
            climate_sections = soup.find_all(['h2', 'h3'], text=re.compile(r'Climate|Weather', re.I))
            
            for section in climate_sections:
                parent = section.find_parent()
                if parent:
                    # Get the next few paragraphs after climate heading
                    next_sibling = section.find_next_sibling()
                    climate_text = ""
                    
                    while next_sibling and next_sibling.name in ['p', 'div']:
                        if next_sibling.name == 'p':
                            climate_text += next_sibling.get_text() + " "
                        next_sibling = next_sibling.find_next_sibling()
                        
                        # Stop if we hit another heading
                        if next_sibling and next_sibling.name in ['h1', 'h2', 'h3', 'h4']:
                            break
                    
                    if climate_text.strip():
                        weather_data['weather_description'] = climate_text.strip()[:500]  # Limit length
                        
                        # Extract specific climate type mentions
                        climate_lower = climate_text.lower()
                        if 'desert' in climate_lower:
                            weather_data['climate_type'] = 'Desert'
                        elif 'arid' in climate_lower:
                            weather_data['climate_type'] = 'Arid'
                        elif 'subtropical' in climate_lower:
                            weather_data['climate_type'] = 'Subtropical'
                        
                        logger.info(f"Extracted climate description for {weather_data['city_name']}")
                        break
                    
        except Exception as e:
            logger.warning(f"Could not extract climate info: {e}")
    
    def _extract_infobox_climate(self, soup, weather_data):
        """Extract climate data from Wikipedia infobox"""
        try:
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    header = row.find('th')
                    data = row.find('td')
                    
                    if header and data:
                        header_text = header.get_text().strip().lower()
                        data_text = data.get_text().strip()
                        
                        if 'climate' in header_text and not weather_data['climate_type']:
                            weather_data['climate_type'] = data_text[:50]  # Limit length
                        elif 'temperature' in header_text and not weather_data['avg_temperature_celsius']:
                            # Extract temperature numbers
                            temp_match = re.search(r'(\d+\.?\d*)', data_text)
                            if temp_match:
                                weather_data['avg_temperature_celsius'] = float(temp_match.group(1))
                                
        except Exception as e:
            logger.warning(f"Could not extract infobox climate: {e}")
    
    def _extract_climate_tables(self, soup, weather_data):
        """Extract data from climate/weather tables"""
        try:
            # Look for climate data tables
            tables = soup.find_all('table', class_=['wikitable', 'climate-table'])
            
            for table in tables:
                caption = table.find('caption')
                table_text = table.get_text().lower()
                
                if (caption and ('climate' in caption.get_text().lower() or 'weather' in caption.get_text().lower())) or \
                   ('temperature' in table_text and 'rainfall' in table_text):
                    
                    # Extract temperature and rainfall data from table
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > 1:
                            row_header = cells[0].get_text().strip().lower()
                            
                            if ('average high' in row_header or 'mean maximum' in row_header) and \
                               not weather_data['avg_temperature_celsius']:
                                # Extract average of high temperatures
                                temps = []
                                for cell in cells[1:13]:  # 12 months max
                                    temp_text = cell.get_text().strip()
                                    temp_match = re.search(r'(\d+\.?\d*)', temp_text)
                                    if temp_match:
                                        temps.append(float(temp_match.group(1)))
                                
                                if temps:
                                    weather_data['avg_temperature_celsius'] = round(sum(temps) / len(temps), 1)
                                    logger.info(f"Extracted average temperature: {weather_data['avg_temperature_celsius']}°C")
                            
                            elif ('rainfall' in row_header or 'precipitation' in row_header) and \
                                 not weather_data['annual_rainfall_mm']:
                                # Extract total annual rainfall
                                rainfalls = []
                                for cell in cells[1:13]:  # 12 months max
                                    rain_text = cell.get_text().strip()
                                    rain_match = re.search(r'(\d+\.?\d*)', rain_text)
                                    if rain_match:
                                        rainfalls.append(float(rain_match.group(1)))
                                
                                if rainfalls:
                                    weather_data['annual_rainfall_mm'] = round(sum(rainfalls), 1)
                                    logger.info(f"Extracted annual rainfall: {weather_data['annual_rainfall_mm']}mm")
                                    
        except Exception as e:
            logger.warning(f"Could not extract climate tables: {e}")
    
    def save_to_database(self, weather_data):
        """Save extracted weather data to SQLite database"""
        try:
            conn = sqlite3.connect('uae_weather.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO weather_data 
                (city_name, latitude, longitude, climate_type, avg_temperature_celsius, 
                 avg_humidity_percent, annual_rainfall_mm, hottest_month, coldest_month, 
                 weather_description, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_data['city_name'],
                weather_data['latitude'],
                weather_data['longitude'],
                weather_data['climate_type'],
                weather_data['avg_temperature_celsius'],
                weather_data['avg_humidity_percent'],
                weather_data['annual_rainfall_mm'],
                weather_data['hottest_month'],
                weather_data['coldest_month'],
                weather_data['weather_description'],
                'Wikipedia'
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Data saved for {weather_data['city_name']}")
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            raise
    
    def extract_all_cities(self):
        """Extract weather data for all UAE cities"""
        logger.info("Starting weather data extraction for all UAE cities")
        self.init_database()
        
        extracted_count = 0
        failed_cities = []
        
        for city_name, url in self.uae_cities.items():
            try:
                weather_data = self.extract_weather_from_wikipedia(city_name, url)
                
                if weather_data:
                    self.save_to_database(weather_data)
                    extracted_count += 1
                    logger.info(f"✅ Successfully processed {city_name}")
                else:
                    failed_cities.append(city_name)
                    logger.error(f"❌ Failed to extract data for {city_name}")
                
            except Exception as e:
                failed_cities.append(city_name)
                logger.error(f"❌ Error processing {city_name}: {e}")
            
            # Rate limiting - be respectful to Wikipedia
            time.sleep(3)
        
        logger.info(f"Extraction completed. Successfully processed {extracted_count}/{len(self.uae_cities)} cities")
        
        if failed_cities:
            logger.warning(f"Failed cities: {failed_cities}")
            
        return extracted_count, failed_cities

    def get_weather_data(self, city_name=None):
        """Retrieve weather data from database"""
        try:
            conn = sqlite3.connect('uae_weather.db')
            cursor = conn.cursor()
            
            if city_name:
                cursor.execute('''
                    SELECT * FROM weather_data 
                    WHERE city_name = ? 
                    ORDER BY extracted_at DESC LIMIT 1
                ''', (city_name,))
            else:
                cursor.execute('''
                    SELECT * FROM weather_data 
                    ORDER BY city_name, extracted_at DESC
                ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []

    def display_summary(self):
        """Display a summary of extracted weather data"""
        data = self.get_weather_data()
        
        if not data:
            print("No weather data found in database.")
            return
            
        print("\n" + "="*60)
        print("UAE CITIES WEATHER DATA SUMMARY")
        print("="*60)
        
        for row in data:
            print(f"""
🏙️  City: {row[1]}
📍 Coordinates: {row[2]}, {row[3]}
🌡️  Climate: {row[4] or 'N/A'}
🌡️  Avg Temperature: {row[5]}°C
🌧️  Annual Rainfall: {row[7]}mm
📝 Description: {(row[10][:100] + '...') if row[10] else 'N/A'}
📅 Last Updated: {row[12]}
{'-'*40}""")

# Usage example and main execution
if __name__ == "__main__":
    extractor = UAEWeatherExtractor()
    
    try:
        # Extract weather data for all cities
        print("🚀 Starting UAE Weather Data Extraction...")
        success_count, failed_cities = extractor.extract_all_cities()
        
        print(f"\n✅ Extraction completed: {success_count}/7 cities successful")
        
        if failed_cities:
            print(f"❌ Failed cities: {failed_cities}")
        
        # Display summary
        extractor.display_summary()
        
    except KeyboardInterrupt:
        print("\n⏹️  Extraction interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        print(f"\n❌ Fatal error occurred: {e}")