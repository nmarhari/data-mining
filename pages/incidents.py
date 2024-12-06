import dash
from dash import html, dcc, Input, Output
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import MinMaxScaler
import folium
import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
module_dir = os.path.join(current_dir, '../', 'functions')
sys.path.append(module_dir)
from traffic_fetcher import fetch_incident_data

dash.register_page(__name__, path="/incidents")
print('\n\n@@ start incidents page @@')

bounding_box = "13.08836,52.33812,13.761,52.6755"
incident_data = fetch_incident_data(bounding_box)

if not incident_data.empty:
    # get and label criticality for clustering
    if 'criticality' in incident_data.columns:
        criticality_mapping = {"minor": 1, "moderate": 2, "major": 3}
        incident_data['criticality_value'] = incident_data['criticality'].map(criticality_mapping).fillna(0)
    else:
        incident_data['criticality_value'] = 0  # default if missing (but shouldnt be)

    # keep lat and long so it does not get modified
    incident_data['original_lat'] = incident_data['lat']
    incident_data['original_lng'] = incident_data['lng']

    # normalize the values used in clustering
    scaler = MinMaxScaler()
    incident_data[['lat', 'lng', 'criticality_value']] = scaler.fit_transform(
        incident_data[['lat', 'lng', 'criticality_value']]
    )

    # cluster w kmeans
    kmeans = KMeans(n_clusters=3, random_state=0)
    incident_data['kmeans_cluster'] = kmeans.fit_predict(
        incident_data[['lat', 'lng', 'criticality_value']]
    )

    # dbscan for noise etc
    dbscan = DBSCAN(eps=0.1, min_samples=3).fit(
        incident_data[['lat', 'lng', 'criticality_value']]
    )
    incident_data['dbscan_cluster'] = dbscan.labels_

    # predefine colors for display based on cluster it was put in
    kmeans_cluster_colors = {0: 'green', 1: 'orange', 2: 'red'}

    # create clustered map with coloring based on which cluster it was in
    def create_combined_incident_map(data, show_gray=True):
        criticality_color_mapping = {
            "low": "green",
            "minor": "yellow",
            "major": "orange",
            "critical": "red",
        }
        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        for _, row in data.iterrows():
            if not show_gray and row['dbscan_cluster'] == -1:
                continue  # skip these points if toggle is off

            # use criticality for the coloring ( blue default if error)
            criticality_color = criticality_color_mapping.get(row['criticality'], 'blue')
            color = 'gray' if row['dbscan_cluster'] == -1 else criticality_color

            popup_content = (
                f"<b>Location:</b> {row['description']}<br>"
                f"<b>Criticality:</b> {row['criticality']}<br>"
                f"<b>Type:</b> {row['incident_type']}<br>"
                f"<b>Start Time:</b> {row['start_time']}<br>"
                f"<b>End Time:</b> {row['end_time']}<br>"
                f"<b>KMeans Cluster:</b> {row['kmeans_cluster']}<br>"
                f"<b>DBSCAN Cluster:</b> {row['dbscan_cluster']}<br>"
                f"<b>Normalized Criticality:</b> {row['criticality_value']:.2f}"
            )
            popup = folium.Popup(popup_content, max_width=400, min_width=200)
            folium.CircleMarker(
                location=[row['original_lat'], row['original_lng']],
                radius=5,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)
        return m._repr_html_()

    # raw map without color or clustering to show difference
    def create_raw_incident_map(data):
        m = folium.Map(location=[52.4500, 13.4050], zoom_start=11)
        for _, row in data.iterrows():
            color = 'blue'

            popup_content = (
                f"<b>Location:</b> {row['description']}<br>"
                f"<b>Criticality:</b> {row['criticality']}<br>"
                f"<b>Type:</b> {row['incident_type']}<br>"
                f"<b>Start Time:</b> {row['start_time']}<br>"
                f"<b>End Time:</b> {row['end_time']}"
            )
            popup = folium.Popup(popup_content, max_width=400, min_width=200)
            folium.CircleMarker(
                location=[row['original_lat'], row['original_lng']],
                radius=5,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=popup
            ).add_to(m)
        return m._repr_html_()

    # preload the maps so its speedy!
    preloaded_incident_maps = {
        "combined_with_gray": create_combined_incident_map(incident_data, show_gray=True),
        "combined_without_gray": create_combined_incident_map(incident_data, show_gray=False),
        "raw": create_raw_incident_map(incident_data),
    }
else: # if errors or whatnot still shows page w/o crashing
    preloaded_incident_maps = {
        "combined_with_gray": "<h3>No incident data available for combined map with gray points.</h3>",
        "combined_without_gray": "<h3>No incident data available for combined map without gray points.</h3>",
        "raw": "<h3>No incident data available for raw map.</h3>",
    }

layout = html.Div(
    [
        html.H1([
            html.A(id='text-center my3', children='Data Mining Techniques Group 5', href="/", style={"text-decoration": "none", "color": "white"})
        ], style={"text-decoration": "none"}),
        html.Div(
            dcc.Dropdown(
                id="incident-map-dropdown",
                options=[
                    {"label": "Combined Incident Map", "value": "combined"},
                    {"label": "Raw Incident Map", "value": "raw"}
                ],
                value="combined",
                className="mb-3"
            ),
            style={"width": "50%", "margin": "auto"}
        ),
        html.Div(
            id="incident-map-container",
            children=[
                html.Iframe(
                    id="incident-map-iframe",
                    srcDoc=preloaded_incident_maps["combined_with_gray"],
                    width="100%",
                    height="750"
                )
            ],
            style={"margin": "auto", "width": "95%", "height": "75%"}
        ),
        html.Div(
            id="gray-points-toggle-container-incidents",
            children=[
                dcc.Checklist(
                    id="gray-points-toggle-incidents",
                    options=[{"label": "Show Gray Points (Noise)", "value": "show_gray"}],
                    value=[""],  # default to not showing gray points
                    style={"margin": "auto", "text-align": "center"}
                )
            ],
            style={"display": "block"}
        ),
    ],
)

@dash.callback(
    [Output("incident-map-iframe", "srcDoc"),
     Output("gray-points-toggle-container-incidents", "style")],
    [Input("incident-map-dropdown", "value"), Input("gray-points-toggle-incidents", "value")]
)
def update_incident_map(selected_view, gray_toggle):
    show_gray = "show_gray" in gray_toggle

    if selected_view == "combined":
        return (
            preloaded_incident_maps["combined_with_gray"] if show_gray else preloaded_incident_maps["combined_without_gray"],
            {"display": "block"}  # show the toggle on block, otherwise none for hiding
        )
    elif selected_view == "raw":
        return preloaded_incident_maps["raw"], {"display": "none"}  # hide the toggle on none
    return "<h3>No data available for the selected view.</h3>", {"display": "none"}
