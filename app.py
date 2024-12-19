import streamlit as st
from streamlit_folium import st_folium
import folium
from shapely.geometry import Point, Polygon
import pandas as pd
import json

# Sample Address Dataset
addresses = pd.DataFrame({
    "Address ID": [1, 2, 3, 4],
    "Address": ["123 Main St", "456 Elm St", "789 Pine St", "101 Oak St"],
    "Latitude": [40.7128, 40.7150, 40.7190, 40.7135],
    "Longitude": [-74.0060, -74.0100, -74.0080, -74.0050]
})

# Streamlit App
st.title("Draw Polygons and Link with Addresses")

# Map for Drawing Polygons
m = folium.Map(location=[40.7128, -74.0060], zoom_start=14)

# Add drawing functionality to the map
from folium.plugins import Draw
draw = Draw(export=True)
draw.add_to(m)

# Display the map
st.write("Draw a polygon on the map and click 'Save' in the drawing toolbar to process it.")
map_data = st_folium(m, width=700, height=500)

# Process Polygon and Link Addresses
if map_data and "last_active_drawing" in map_data and map_data["last_active_drawing"]:
    st.write("Polygon Coordinates:", map_data["last_active_drawing"]["geometry"]["coordinates"])
    polygon_coords = map_data["last_active_drawing"]["geometry"]["coordinates"][0]
    
    # Create a Polygon
    polygon = Polygon([(coord[0], coord[1]) for coord in polygon_coords])

    # Check which addresses are inside the polygon
    linked_addresses = []
    for _, row in addresses.iterrows():
        point = Point(row["Longitude"], row["Latitude"])
        if polygon.contains(point):
            linked_addresses.append(row)

    # Display Linked Addresses
    if linked_addresses:
        st.write("Addresses inside the polygon:")
        st.dataframe(pd.DataFrame(linked_addresses))
    else:
        st.write("No addresses found inside the polygon.")
