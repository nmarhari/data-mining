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
from traffic_fetcher import fetch_flow_data 

dash.register_page(__name__, path="/map")
print('\n\n@@ app start @@')

# fetch traffic data
bounding_box = "13.08836,52.33812,13.761,52.6755"  # berlin germany (HERE api most data i think)
traffic_data = fetch_flow_data(bounding_box)

if not traffic_data.empty:
    # k means on the location and jam factor
    kmeans = KMeans(n_clusters=3, random_state=0)
    traffic_data['kmeans_cluster'] = kmeans.fit_predict(traffic_data[['lat', 'lng', 'jam_factor']])

    # dbscan to eliminate noise/enhance
    dbscan = DBSCAN(eps=0.01, min_samples=5).fit(traffic_data[['lat', 'lng']])
    traffic_data['dbscan_cluster'] = dbscan.labels_

    noise_count = (traffic_data['dbscan_cluster'] == -1).sum()
    cluster_count = traffic_data['dbscan_cluster'].nunique() - (1 if -1 in traffic_data['dbscan_cluster'].unique() else 0)

    print(f"DBSCAN Clustering Results:")
    print(f" - Total Points: {len(traffic_data)}")
    print(f" - Noise Points: {noise_count}")
    print(f" - Clusters Formed: {cluster_count}")

    # average the jam for the clusters
    kmeans_avg_jam_factors = traffic_data.groupby('kmeans_cluster')['jam_factor'].mean().sort_values()

    # k means to color the clusters
    kmeans_sorted_clusters = kmeans_avg_jam_factors.index.tolist()
    kmeans_cluster_colors = {kmeans_sorted_clusters[0]: 'green',  # lowest jam factor
                              kmeans_sorted_clusters[1]: 'orange',  # medium jam factor
                              kmeans_sorted_clusters[2]: 'red'}     # highest jam factor

    def create_clustered_dot_map(data, show_gray=True):
        # filter noise
        if not show_gray:
            data = data[data['dbscan_cluster'] != -1]  # data without the noise

        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        
        for _, row in data.iterrows():
            # kmeans color or noise/gray, default blue if error
            color = 'gray' if row['dbscan_cluster'] == -1 else kmeans_cluster_colors.get(row['kmeans_cluster'], 'blue')
            popup_content = (
                f"<b>Location:</b> {row['description']}<br>"
                f"<b>Speed:</b> {row['speed']} km/h<br>"
                f"<b>Jam Factor:</b> {row['jam_factor']}<br>"
                f"<b>KMeans Cluster:</b> {row['kmeans_cluster']}<br>"
                f"<b>DBSCAN Cluster:</b> {row['dbscan_cluster']}"
            )
            popup = folium.Popup(popup_content, max_width=400, min_width=200)

            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=5,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)
        return m._repr_html_()

    def create_clustered_heatmap(data):
        clustered_data = data[data['dbscan_cluster'] != -1]  # Exclude noise (-1 cluster)
        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        heat_data = [
            [row['lat'], row['lng'], row['jam_factor']]
            for _, row in clustered_data.iterrows()
            if row['jam_factor'] > 0
        ]
        HeatMap(heat_data, min_opacity=0.5, radius=15, blur=10).add_to(m)
        return m._repr_html_()

    def create_dot_map(data):
        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        for _, row in data.iterrows():
            popup_content = (
                f"<b>Location:</b> {row['description']}<br>"
                f"<b>Speed:</b> {row['speed']} km/h<br>"
                f"<b>Free Flow Speed:</b> {row['free_flow_speed']} km/h<br>"
                f"<b>Jam Factor:</b> {row['jam_factor']}"
            )
            popup = folium.Popup(popup_content, max_width=400, min_width=200)

            folium.CircleMarker(
                location=[row['lat'], row['lng']],
                radius=5,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)
        return m._repr_html_()

    def create_heatmap(data):
        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        heat_data = [
            [row['lat'], row['lng'], row['jam_factor']]
            for _, row in data.iterrows()
            if row['jam_factor'] > 0
        ]
        HeatMap(heat_data, min_opacity=0.5, radius=15, blur=10).add_to(m)
        return m._repr_html_()

    # preload maps for speedy rendering
    print('@ preloading maps @')
    preloaded_maps = {
        "clustered_dot_with_gray": create_clustered_dot_map(traffic_data, show_gray=True),  # w/ noise
        "clustered_dot_without_gray": create_clustered_dot_map(traffic_data, show_gray=False),  # w/o
        "clustered_heatmap": create_clustered_heatmap(traffic_data),  
        "dot": create_dot_map(traffic_data),  
        "heatmap": create_heatmap(traffic_data),  
    }   
    print('@ preloading complete @')
else:
    # no traffic data
    preloaded_maps = {
        "clustered_dot": "<h3>No clustered dot map data available.</h3>",
        "clustered_heatmap": "<h3>No clustered heatmap data available.</h3>",
        "dot": "<h3>No dot map data available.</h3>",
        "heatmap": "<h3>No heatmap data available.</h3>",
    }
print("@@ app load complete @@")

layout = html.Div(
    [
        html.H1([
            html.A(id='text-center my3', children='Data Mining Techniques Group 5', href="/", style={"text-decoration": "none", "color": "white"})
        ], style={"text-decoration": "none"}),
        html.Div(
            dcc.Dropdown(
                id="map-view-dropdown",
                options=[
                    {"label": "Clustered Dot Map", "value": "clustered_dot"},
                    {"label": "Dot Map", "value": "dot"},
                    {"label": "Clustered Heatmap", "value": "clustered_heatmap"},
                    {"label": "Heatmap", "value": "heatmap"},
                ],
                value="clustered_dot", 
                className="mb-3"
            ),
            style={"width": "50%", "margin": "auto"}
        ),
        html.Div(
            id="map-container",
            children=[
                html.Iframe(
                    id="map-iframe",
                    srcDoc=preloaded_maps["clustered_dot_with_gray"],  # Default to clustered dot map with gray points
                    width="100%",
                    height="700"
                )
            ],
            style={"margin": "auto", "width": "95%", "height": "75%"}
        ),
        html.Div(
            id="gray-points-toggle-container",
            children=[
                dcc.Checklist(
                    id="gray-points-toggle",
                    options=[{"label": "Show Gray Points (Noise)", "value": "show_gray"}],
                    value=[],  # default to not showing noise points
                    style={"margin": "auto", "text-align": "center"}
                )
            ],
            style={"display": "block"}  # show toggle for noise points
        ),
    ],
)

# update map on selection
@dash.callback(
    [Output("map-iframe", "srcDoc"),
     Output("gray-points-toggle-container", "style")],
    [Input("map-view-dropdown", "value"), Input("gray-points-toggle", "value")]
)
def update_map_view(selected_view, gray_toggle):
    # show the noise points
    show_gray = "show_gray" in gray_toggle
    
    if selected_view == "clustered_dot":
        # show/hide noise points toggle
        return (
            preloaded_maps["clustered_dot_with_gray"] if show_gray else preloaded_maps["clustered_dot_without_gray"],
            {"display": "block"}
        )
    elif selected_view == "clustered_heatmap":
        return preloaded_maps["clustered_heatmap"], {"display": "none"} 
    elif selected_view == "dot":
        return preloaded_maps["dot"], {"display": "none"}
    elif selected_view == "heatmap":
        return preloaded_maps["heatmap"], {"display": "none"}  
    return "<h3>No data available for the selected view.</h3>", {"display": "none"}