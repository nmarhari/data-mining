import os
from traffic_fetcher import fetch_traffic_data


bounding_box = "13.08836,52.33812,13.761,52.6755" 
traffic_data = fetch_traffic_data(bounding_box)
print(traffic_data.head())
print(traffic_data)