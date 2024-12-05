import dash
from dash import html
import pandas as pd
from sklearn.cluster import KMeans
import folium
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(current_dir, '../', 'functions')
sys.path.append(module_dir)
# print(sys.path)
from traffic_fetcher import fetch_traffic_data

# Register this page with Dash Pages
dash.register_page(__name__, path="/map")

bounding_box = "13.08836,52.33812,13.761,52.6755"
traffic_data = fetch_traffic_data(bounding_box)

if not traffic_data.empty:
    # Refine clustering by including more traffic-relevant features
    kmeans = KMeans(n_clusters=3, random_state=0)
    traffic_data['cluster'] = kmeans.fit_predict(traffic_data[['lat', 'lng', 'jam_factor']])

    # Define colors based on Jam Factor
    def get_color(jam_factor):
        if jam_factor <= 3:
            return 'green'  # Low congestion
        elif jam_factor <= 7:
            return 'orange'  # Medium congestion
        else:
            return 'red'  # High congestion

    # Generate the Folium map
    def create_map(data):
        # Initialize the map
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=10)

        # Add traffic data points to the map
        for _, row in data.iterrows():
            color = get_color(row['jam_factor'])  # Get color based on Jam Factor
            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=10,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=(
                    f"Location: {row['description']}<br>"
                    f"Speed: {row['speed']} km/h<br>"
                    f"Free Flow Speed: {row['free_flow_speed']} km/h<br>"
                    f"Jam Factor: {row['jam_factor']}<br>"
                    f"Cluster: {row['cluster']}"
                )
            ).add_to(m)

        return m._repr_html_()

    # Map as an HTML iframe
    map_html = create_map(traffic_data)
else:
    map_html = "<h3>No traffic data available for the selected area.</h3>"

# Layout for the map page
layout = html.Div(
    [
        html.H1([
            html.A(id='text-center my3', children='Data Mining Techniques Group 5', href="/", style={"text-decoration": "none", "color": "white"})
        ], style={"text-decoration": "none"}),
        html.Div(
            html.Iframe(
                srcDoc=map_html,
                width="100%",
                height="750"
            ),
            style={"margin": "auto", "width": "95%", "height": "75%"}
        )
    ],
)