import requests
from bs4 import BeautifulSoup as bs
import os
import unicodedata
import pandas as pd
# url = 'https://en.wikipedia.org/wiki/Abu_Dhabi'

# page = requests.get(url)

# if page.status_code == 200:
#     print("Webpage content successfully fetched!")
# else:
#     print("Failed to fetch the webpage content. Check the URL or your internet connection.")

# ob = Bf(page.text, 'html.parser')

# tag = ob.find('h1', class_="firstHeading mw-first-heading")

# # print(ob)

# # tag = ob.h1
# print(tag.prettify())  # Output: 4-6


def extract_city_informatin(html_object):
    dict_citiy = {}

    city_name = html_object.h1.get_text()
    dict_citiy['City_name'] = city_name
    area_element_MC = html_object.select_one('.infobox-label:-soup-contains("Megacity") + .infobox-data')
    area_element_C = html_object.select_one('.infobox-label:-soup-contains("City") + .infobox-data')
    elevation_element = html_object.select_one('.infobox-label:-soup-contains("Elevation") + .infobox-data')
    metro = html_object.select_one('.infobox-label:-soup-contains("Metro") + .infobox-data')
    population = html_object.select_one('.mergedtoprow:-soup-contains("Population")')
    latitude = html_object.select_one('.latitude')
    longitude = html_object.select_one('.longitude')


    if area_element_MC:
        dict_citiy['City_size_Km2'] = unicodedata.normalize('NFC', area_element_MC.get_text(strip=True))
    if area_element_C:
        dict_citiy['City_size_Km2'] = unicodedata.normalize('NFC', area_element_C.get_text(strip=True))
    if elevation_element: 
        dict_citiy['Elevation_in_M'] = unicodedata.normalize('NFC', elevation_element.get_text(strip=True)) 
    if population:
        dict_citiy['Population'] = unicodedata.normalize('NFC', population.find_next('td').get_text(strip=True))
    if metro:
        dict_citiy['Metro_Km2'] = unicodedata.normalize('NFC', metro.get_text(strip=True))
    if latitude:
        dict_citiy['Latitude'] = unicodedata.normalize('NFC', latitude.get_text(strip=True))
    if longitude:
        dict_citiy['Longitude'] = unicodedata.normalize('NFC', longitude.get_text(strip=True))

    return dict_citiy


def extract_city_info_api(city):
    api_key = os.getenv("GOBII_API_KEY")
    if not api_key:
        print("GOBII_API_KEY not set in environment.")
        return

    url = "https://gobii.ai/api/v1/tasks/browser-use/"
    wiki_url = f"https://en.wikipedia.org/wiki/Abu Dhabi"
    prompt = (
        f"Go to {wiki_url} and return the following as JSON: "
        "city_name, area_megacity, area_city, elevation, metro_area, population, latitude, longitude."
    )
    output_schema = {
        "type": "object",
        "properties": {
            "city_name": {"type": "string"},
            "area_megacity": {"type": "string"},
            "area_city": {"type": "string"},
            "elevation": {"type": "string"},
            "metro_area": {"type": "string"},
            "population": {"type": "string"},
            "latitude": {"type": "string"},
            "longitude": {"type": "string"}
        },
        "required": [
            "city_name", "area_megacity", "area_city", "elevation",
            "metro_area", "population", "latitude", "longitude"
        ],
        "additionalProperties": False
    }
    data = {
        "prompt": prompt,
        "output_schema": output_schema,
        "wait": 300
    }
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200,201]:
        print("API Response:", response.json())
    else:
        print(f"API Error: {response.status_code} - {response.text}")

    print



def main():
    cities = ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Fujairah", "Ras Al Khaimah", "Umm Al Quwain"]
    # cities = ["Abu Dhabi"]
    list_of_dict = []
    for city in cities:
        url = f'https://en.wikipedia.org/wiki/{city}'
        try:
            page = requests.get(url, timeout=10)
            if page.status_code == 200:
                html_object = bs(page.text, 'html.parser')
                list_of_dict.append(extract_city_informatin(html_object)) 
            else:
                print(f"Failed to fetch data for {city}. HTTP Status Code: {page.status_code}")
        except requests.exceptions.RequestException as e:
                print(f"An error occurred while fetching data for {city}: {e}")
        
    # for i in list_of_dict:
    #     print(i)
    
    df = pd.DataFrame(list_of_dict)
    df.to_csv('all_city_data.csv', index=False)
    print("Data saved to all_city_data.csv")
    # for i in list_of_dict:
    #     for city in cities:
    #         print(i)

if __name__ == "__main__":
    main()