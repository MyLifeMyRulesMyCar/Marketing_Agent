import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY")


def fetch_trends(keyword, country, time_range):
    url = "https://serpapi.com/search"

    params = {
        "engine": "google_trends",
        "q": keyword,
        "geo": country,
        "date": time_range,
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error fetching {keyword}: {response.text}")
        return None

    return response.json()
