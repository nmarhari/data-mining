import requests
import pandas as pd
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("HERE_API_KEY")

def fetch_traffic_data(bounding_box):
    base_url = "https://data.traffic.hereapi.com/v7/"
    endpoints = {"flow": "flow", "incidents": "incidents"}
    params = {
        "apiKey": API_KEY,
        "in": "bbox:"+bounding_box,
        "locationReferencing": "shape",
    }
    all_data = []

    print(params)
    response = requests.get
    for endpoint, url_suffix in endpoints.items():
        response = requests.get(base_url + url_suffix, params=params)
        print(f"Fetching {endpoint} data: {response.status_code}")
        # print(response.json())
        if response.status_code == 200:
            response_json = response.json()

            for result in response_json.get("results", []):
                # Extract location and traffic details
                location = result.get("location", {})
                current_flow = result.get("currentFlow", {})
                shape = location.get("shape", {}).get("links", [{}])

                # Add traffic data entry
                traffic_entry = {
                    "type": endpoint,
                    "description": location.get("description", "Unknown Location"),
                    "length": location.get("length", 0),
                    "speed": current_flow.get("speed", 0),
                    "free_flow_speed": current_flow.get("freeFlow", 0),
                    "jam_factor": current_flow.get("jamFactor", 0),
                    "lat": shape[0].get("points", [{}])[0].get("lat", 0) if shape else 0,
                    "lng": shape[0].get("points", [{}])[0].get("lng", 0) if shape else 0,
                    "time_updated": response_json.get("sourceUpdated", "Unknown Time"),
                }

                all_data.append(traffic_entry)
        else:
            print(f"Failed to fetch {endpoint} data: {response.status_code}")
            print(response.text)

    return pd.DataFrame(all_data)