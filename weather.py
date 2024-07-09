import requests
weather_api_key = 'fc76c33ae185424893f71443240407'


def get_weather(city):
    """Fetch current weather information for a city using OpenWeatherMap API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': 'weather_API_key',
        'units': 'metric'  # For Celsius
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for bad response status

        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather_description}. The temperature is {temperature} degrees Celsius."

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except KeyError as key_err:
        return f"Unexpected response format: {key_err}"
    except Exception as e:
        return f"An error occurred: {e}"

