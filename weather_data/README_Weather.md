# UAE Weather Data Extraction Pipeline

This system extracts weather and climate data from Wikipedia for the seven major cities in the UAE and stores it in a structured database for analysis.

## Features

- 🌐 **Wikipedia Scraping**: Extracts climate data from Wikipedia pages
- 🗄️ **Database Storage**: SQLite database with structured schema
- 📊 **Data Validation**: Cleans and validates extracted data
- ⏰ **Scheduling**: Automated data collection
- 🔄 **API Backup**: Optional OpenWeatherMap API integration
- 📝 **Logging**: Comprehensive logging and error handling
- 🛡️ **Rate Limiting**: Respectful requests to Wikipedia

## UAE Cities Covered

1. **Abu Dhabi** (Capital)
2. **Dubai**
3. **Sharjah**
4. **Ajman**
5. **Ras Al Khaimah**
6. **Fujairah**
7. **Umm Al Quwain**

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. (Optional) Get OpenWeatherMap API key:
   - Visit https://openweathermap.org/api
   - Sign up for a free account
   - Get your API key

## Usage

### Manual Extraction

Run a single extraction of all UAE cities:

```bash
# Run the main extractor
python weather_extractor.py

# Or run via scheduler in manual mode
python scheduler.py manual
```

### Scheduled Extraction

Start the automated scheduler:

```bash
python scheduler.py
```

**Default Schedule:**
- Wikipedia extraction: Daily at 9 AM, Weekly on Sunday at 6 AM
- API collection: Every 6 hours (if API key provided)

### API Backup (Optional)

To enable OpenWeatherMap API backup:

1. Get your API key from https://openweathermap.org/api
2. Edit `scheduler.py` and add your API key:
```python
API_KEY = "your_actual_api_key_here"
```

## Database Schema

### Main Weather Data Table (`weather_data`)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city_name | TEXT | UAE city name |
| latitude | REAL | Latitude coordinate |
| longitude | REAL | Longitude coordinate |
| climate_type | TEXT | Climate classification |
| avg_temperature_celsius | REAL | Average temperature |
| avg_humidity_percent | REAL | Average humidity |
| annual_rainfall_mm | REAL | Annual rainfall |
| hottest_month | TEXT | Hottest month |
| coldest_month | TEXT | Coldest month |
| weather_description | TEXT | Climate description |
| data_source | TEXT | Data source (Wikipedia) |
| extracted_at | TIMESTAMP | Extraction timestamp |

### API Weather Data Table (`current_weather_api`)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city_name | TEXT | UAE city name |
| temperature | REAL | Current temperature |
| humidity | REAL | Current humidity |
| pressure | REAL | Atmospheric pressure |
| weather_condition | TEXT | Current weather condition |
| wind_speed | REAL | Wind speed |
| visibility | REAL | Visibility |
| data_source | TEXT | Data source (OpenWeatherMap) |
| timestamp | TIMESTAMP | Collection timestamp |

## Data Extraction Process

1. **Wikipedia Scraping**:
   - Extracts coordinates from geo microformat
   - Parses climate sections and infoboxes
   - Extracts data from climate tables
   - Cleans and validates extracted data

2. **Data Storage**:
   - Stores in SQLite database
   - Prevents duplicates with unique constraints
   - Logs all operations

3. **Error Handling**:
   - Network timeouts and retries
   - Data validation
   - Comprehensive logging

## Rate Limiting

The system respects Wikipedia's servers with:
- 2-3 second delays between requests
- Proper User-Agent headers
- Timeout handling

## Example Output

```
🏙️  City: Dubai
📍 Coordinates: 25.2048, 55.2708
🌡️  Climate: Subtropical desert
🌡️  Avg Temperature: 28.5°C
🌧️  Annual Rainfall: 97.8mm
📝 Description: Dubai has a hot desert climate. The weather in Dubai is warm and sunny...
📅 Last Updated: 2025-05-24 09:15:32
```

## File Structure

```
weather_data/
├── weather_extractor.py      # Main extraction class
├── weather_api_backup.py     # API backup integration
├── scheduler.py              # Scheduling system
├── requirements.txt          # Dependencies
├── README_Weather.md         # This documentation
└── uae_weather.db           # SQLite database (created automatically)
```

## Troubleshooting

### Common Issues

1. **Network Errors**:
   - Check internet connection
   - Wikipedia might be temporarily unavailable
   - Rate limiting in effect

2. **Database Errors**:
   - Ensure write permissions in directory
   - Check disk space

3. **Extraction Failures**:
   - Wikipedia page structure may have changed
   - Check logs for specific errors

### Logs

Check `weather_scheduler.log` for detailed execution logs when using the scheduler.

## Contributing

To add new cities or improve extraction:

1. Add city URLs to `uae_cities` dictionary in `UAEWeatherExtractor`
2. Update coordinates in `WeatherAPIBackup` if using API
3. Test extraction with new cities
4. Update documentation

## Notes

- Data is extracted for educational and analysis purposes
- Respects Wikipedia's robots.txt and usage policies
- API usage requires free OpenWeatherMap account
- Database file (`uae_weather.db`) is created automatically