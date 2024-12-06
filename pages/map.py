import dash
from dash import html, dcc, Input, Output
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
import folium
from folium.plugins import HeatMap
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(current_dir, '../', 'functions')
sys.path.append(module_dir)
from traffic_fetcher import fetch_flow_data  # Assuming traffic_fetcher.py is correctly implemented

# Register this page with Dash Pages
dash.register_page(__name__, path="/map")

# Fetch traffic data
bounding_box = "13.08836,52.33812,13.761,52.6755"  # Berlin bounding box
traffic_data = fetch_flow_data(bounding_box)

if not traffic_data.empty:
    # Apply clustering using KMeans
    kmeans = KMeans(n_clusters=3, random_state=0)
    traffic_data['kmeans_cluster'] = kmeans.fit_predict(traffic_data[['lat', 'lng', 'jam_factor']])

    # Calculate the average jam factor for each cluster
    cluster_avg_jam_factors = traffic_data.groupby('kmeans_cluster')['jam_factor'].mean().sort_values()

    # Map clusters to colors based on the average jam factor ranking
    sorted_clusters = cluster_avg_jam_factors.index.tolist()
    cluster_colors = {sorted_clusters[0]: 'green',  # Lowest jam factor
                      sorted_clusters[1]: 'orange',  # Medium jam factor
                      sorted_clusters[2]: 'red'}     # Highest jam factor

    # Define the clustering map
    def create_cluster_map(data):
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=10)
        for _, row in data.iterrows():
            color = cluster_colors.get(row['kmeans_cluster'], 'blue')  # Default to blue for unexpected clusters
            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=2,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=(
                    f"Location: {row['description']}<br>"
                    f"Speed: {row['speed']} km/h<br>"
                    f"Jam Factor: {row['jam_factor']}<br>"
                    f"Cluster: {row['kmeans_cluster']}<br>"
                    f"Average Jam Factor (Cluster): {cluster_avg_jam_factors[row['kmeans_cluster']]:.2f}"
                )
            ).add_to(m)
        return m._repr_html_()

    # Define the heatmap
    def create_heatmap(data):
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=10)
        heat_data = [
            [row['lat'], row['lng'], row['jam_factor']]
            for _, row in data.iterrows()
            if row['jam_factor'] > 0
        ]
        HeatMap(heat_data, min_opacity=0.5, max_val=10, radius=15, blur=10).add_to(m)
        return m._repr_html_()

    # Define the dot map (original view)
    def create_dot_map(data):
        m = folium.Map(location=[52.5200, 13.4050], zoom_start=10)
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=5,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=(
                    f"Location: {row['description']}<br>"
                    f"Speed: {row['speed']} km/h<br>"
                    f"Free Flow Speed: {row['free_flow_speed']} km/h<br>"
                    f"Jam Factor: {row['jam_factor']}"
                )
            ).add_to(m)
        return m._repr_html_()
else:
    traffic_data = pd.DataFrame(columns=['lat', 'lng', 'jam_factor', 'description', 'speed', 'free_flow_speed'])
    map_html = "<h3>No traffic data available for the selected area.</h3>"

# Layout for the map page
layout = html.Div(
    [
        html.H1([
            html.A(id='text-center my3', children='Data Mining Techniques Group 5', href="/", style={"text-decoration": "none", "color": "white"})
        ], style={"text-decoration": "none"}),
        html.Div(
            dcc.Dropdown(
                id="map-view-dropdown",
                options=[
                    {"label": "Clustering Map", "value": "cluster"},
                    {"label": "Heatmap", "value": "heatmap"},
                    {"label": "Dot Map", "value": "dot"}
                ],
                value="cluster",  # Default view
                className="mb-3"
            ),
            style={"width": "50%", "margin": "auto"}
        ),
        html.Div(
            id="map-container",
            children=[
                html.Iframe(
                    id="map-iframe",
                    srcDoc=create_cluster_map(traffic_data),  # Default view
                    width="100%",
                    height="750"
                )
            ],
            style={"margin": "auto", "width": "95%", "height": "75%"}
        )
    ],
)

# Callback to update the map based on the dropdown selection
@dash.callback(
    Output("map-iframe", "srcDoc"),
    Input("map-view-dropdown", "value")
)
def update_map_view(selected_view):
    if selected_view == "dot":
        return create_dot_map(traffic_data)
    elif selected_view == "heatmap":
        return create_heatmap(traffic_data)
    elif selected_view == "cluster":
        return create_cluster_map(traffic_data)
    return "<h3>No data available for the selected view.</h3>"