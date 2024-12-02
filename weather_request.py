import logging as log
from pprint import pprint
import requests 
# import geocoder 


def forecast(search_location):
    geocode_error, latlng = geocode(search_location)
    if geocode_error:
        return geocode_error, None 
    
    forcast_url_error, forecast_url, city_string = request_forecast_url_and_city(latlng)
    if forcast_url_error:
        return forcast_url_error, None 
    
    weather_error, weather_response = request_weather(forecast_url)
    if weather_error:
        return weather_error, None 
    
    weather_object_error, weather_objects = simplify_response(latlng, search_location, city_string, weather_response)
    if weather_object_error:
        return weather_object_error, None 
    
    return None, weather_objects 


def geocode(location_string):

    try:
        url = f'https://nominatim.openstreetmap.org/search?q={location_string}&format=jsonv2&addressdetails=1&limit=1'
        headers = {'User-Agent': 'ITEC 2545 Weather Server'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            first = data[0]
            lat = first['lat']
            lon = first['lon']
            return None, [lat, lon]
        else:
            return f'No location found for {location_string}', None
    except Exception as e:
        log.exception(f'Unable to geocode {location_string}', exc_info=True)
        return 'Can\'t get location', None 



def geocode_nope(location):
    try:
        result = geocoder.osm(location)
        print(result)
        if result.ok:
            return None, result.latlng
        else:
            return f'No results found for {location}', None 
    except Exception as e:
        log.exception(f'Unable to geocode {location}', exc_info=True)
        return 'Can\'t get location', None 


def request_forecast_url_and_city(latlng):
    latitude, longitude = latlng
    try:
        points_url = f'https://api.weather.gov/points/{latitude},{longitude}'
        response = requests.get(points_url)
        response.raise_for_status()
        json_points_info = response.json()
        forcast_url = json_points_info['properties']['forecast']
        city_state_props = json_points_info['properties']['relativeLocation']['properties']
        city_string = f"{city_state_props['city']}, {city_state_props['state']}"
        return None, forcast_url, city_string
    except Exception as e:
        log.exception(f'Unable to fetch forecast URL for {latlng}. Locations must be in the USA', exc_info=True)
        return 'Can\'t get weather for this location. Locations must be in the USA', None, None


def request_weather(forecast_url):
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        json_weather = response.json()
        return None, json_weather
    except Exception as e:
        log.exception(f'Unable to fetch forecast for {forecast_url}. Locations must be in the USA', exc_info=True)
        return 'Can\'t get weather forecast', None 


def simplify_response(latlng, search_term, nws_forecast_location, original_nws_response):
    
    """
    return dictionary in the form

    {
        'attribution': {
            'geocoding': 'Geocoding by OpenStreetMap Nominatim API service. OpenStreetMap data made available under the Open Database License https://www.openstreetmap.org/copyright',
            'weather': 'Weather data from the National Weather Service'
        },
        "location": { 
            "searchTerm": "minneapolis mn",
            "forecastCity: "Minneapolis, MN",
            "latitude": 45,
            "longitude": -93
        },
        "weather": [
            {
                "forecastPeriod": "Monday",
                "temperature": 45,
                "windSpeed": "12 to 20 mph",
                "windDirection": "SW",
                "details": "Sunny with some clouds"
            },
            {
                "forecastPeriod": "Monday Night",
                "temperature": -1,
                "windSpeed": 12,
                "windDirection": "SW",
                "details": "Cold with some clouds"
            },
            ... etc

        ]
    }
    
    """

    try:
        periods = original_nws_response['properties']['periods']
        weather = [ {
                'forecastPeriod': period['name'], 
                'temperature': period['temperature'],
                'windSpeed': period['windSpeed'],
                'windDirection': period['windDirection'],
                'details': period['detailedForecast']
            } for period in periods ]
        
        simplified_response = {
            'attributions': {
                'geocoding': 'Geocoding by OpenStreetMap Nominatim API service. OpenStreetMap data made available under the Open Database License https://www.openstreetmap.org/copyright',
                'weather': 'Weather data from the National Weather Service'
            },
            'location': {
                'searchTerm': search_term,
                'forecastCity': nws_forecast_location,
                'latitude': latlng[0],
                'longitude': latlng[1],
            },
            'weather': weather
        }

        return None, simplified_response

    except Exception as e:
        log.exception(f'Error processing NWS response for {search_term} {latlng}', exc_info=True)
        return 'Can\'t get weather forecast', None 

if __name__ == '__main__':
    pprint(forecast('Minneapolis, MN'))
    print(forecast('sdfsgfijspogj;xprgjpo'))