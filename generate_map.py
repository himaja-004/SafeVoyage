import pandas as pd
import openrouteservice
import folium
from folium.plugins import MarkerCluster
from math import radians, sin, cos, sqrt, atan2
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv()


file_path = os.getenv("DATASET_PATH")
df = pd.read_excel(file_path)


df["lat"] = df["lat"].astype(str).str.replace(r"[^\d.-]", "", regex=True).astype(float)
df["lon"] = df["lon"].astype(str).str.replace(r"[^\d.-]", "", regex=True).astype(float)


df = df[(df["lat"].between(-90, 90)) & (df["lon"].between(-180, 180))]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def get_marker_color(score):
    return {"risk": "red", "moderate": "orange", "safe": "green"}.get(score.lower(), "blue")


def get_coordinates(area_name):
    match = df[df["AREA"].str.lower() == area_name.lower()]
    if not match.empty:
        return match.iloc[0]["lat"], match.iloc[0]["lon"]
    else:
        raise ValueError(f"Location '{area_name}' not found in dataset.")


def calculate_route_safety(route_coords):
    safety_scores = []

    for route_lat, route_lon in route_coords:
        try:
            nearby_points = df[df.apply(lambda row: haversine(route_lat, route_lon, row['lat'], row['lon']) < 0.1, axis=1)]

            if nearby_points.empty:
                distances = df.apply(lambda row: haversine(route_lat, route_lon, row['lat'], row['lon']), axis=1)
                nearest_idx = distances.idxmin()
                nearest_score = df.loc[nearest_idx, 'score']
                safety_score = {"safe": 100, "moderate": 50, "risk": 0}.get(nearest_score.lower(), 50)
                safety_scores.append(safety_score)
            else:
                route_score = nearby_points['score'].map(lambda score: {"safe": 100, "moderate": 50, "risk": 0}.get(score.lower(), 50)).mean()
                safety_scores.append(route_score)
        except Exception as e:
            print(f"Error calculating safety for point ({route_lat}, {route_lon}): {e}")
            safety_scores.append(50)

    if not safety_scores:
        return None
    else:
        avg_safety_score = sum(safety_scores) / len(safety_scores)
        return avg_safety_score


def generate_route_map(source_name, destination_name):
    source_lat, source_lon = get_coordinates(source_name)
    destination_lat, destination_lon = get_coordinates(destination_name)

    API_KEY = os.getenv("ORS_API_KEY")
    client = openrouteservice.Client(key=API_KEY)

    mid_lat, mid_lon = (source_lat + destination_lat) / 2, (source_lon + destination_lon) / 2
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)

    
    folium.Marker([source_lat, source_lon], popup=source_name, icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker([destination_lat, destination_lon], popup=destination_name, icon=folium.Icon(color="blue")).add_to(m)

    route_request = client.directions(
        coordinates=[[source_lon, source_lat], [destination_lon, destination_lat]],
        profile="driving-car",
        format="geojson",
        alternative_routes={"share_factor": 0.6, "target_count": 3},
        validate=False
    )

    route_colors = ["blue", "red", "green", "purple", "orange"]
    print(f"Found {len(route_request['features'])} alternative routes.")

    for i, route in enumerate(route_request["features"]):
        route_coords = [(point[1], point[0]) for point in route["geometry"]["coordinates"]]
        print(f"Route {i} has {len(route_coords)} points.")
        safety_percentage = calculate_route_safety(route_coords)

        folium.PolyLine(route_coords, color=route_colors[i % len(route_colors)], weight=5, opacity=0.8).add_to(m)

        if route_coords:
            midpoint = route_coords[len(route_coords) // 2]
            if safety_percentage is not None:
                popup_text = f"Safety: {safety_percentage:.2f}%"
                icon_color = 'cadetblue'
            else:
                popup_text = "Safety: Unknown"
                icon_color = 'gray'

            folium.Marker(
                location=midpoint,
                popup=popup_text,
                icon=folium.Icon(color=icon_color)
            ).add_to(m)
        else:
            print(f"Route {i} has no valid coordinates to mark.")

    
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df.iterrows():
        color = get_marker_color(row["score"])
        popup_html = f"<b>Risk Level:</b> {row['score']}"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color)
        ).add_to(marker_cluster)

    m.save("templates/route_map.html")

