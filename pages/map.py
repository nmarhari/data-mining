import dash
from dash import html
import pandas as pd
from sklearn.cluster import KMeans
import folium

# Register this page with Dash Pages
dash.register_page(__name__, path="/map")

# Sample traffic data
traffic_data = pd.DataFrame({
    'latitude': [40.712776, 34.052235, 41.878113, 29.760427, 39.739235],
    'longitude': [-74.005974, -118.243683, -87.629799, -95.369804, -104.990250],
    'congestion_level': [0.9, 0.7, 0.8, 0.6, 0.5]
})

# Apply clustering
kmeans = KMeans(n_clusters=2, random_state=0)
traffic_data['cluster'] = kmeans.fit_predict(traffic_data[['latitude', 'longitude']])
print(traffic_data['cluster'].unique())
# Generate the Folium map
def create_map(data):
    # Initialize the map
    m = folium.Map(location=[40.712776, -74.005974], zoom_start=4)

    # Define colors explicitly for two clusters
    cluster_colors = {0: 'red', 1: 'blue'}

    # Add clustered points to the map
    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=10,
            color=cluster_colors[row['cluster']],  # Use the cluster_colors dictionary
            fill=True,
            fill_opacity=0.7,
            popup=f"Cluster: {row['cluster']}\nCongestion: {row['congestion_level']}"
        ).add_to(m)

    return m._repr_html_()

# Map as an HTML iframe
map_html = create_map(traffic_data)

# Layout for the map page
layout = html.Div(
    [
        html.H1("Traffic Clustering Map", className="text-center my-3"),
        html.Div(
            html.Iframe(
                srcDoc=map_html,
                width="100%",
                height="600"
            ),
            style={"margin": "auto", "width": "80%"}
        )
    ]
)