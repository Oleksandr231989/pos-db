import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from shapely.geometry import Point, Polygon
import pandas as pd

# Sample Address Dataset (replace this with your real dataset)
addresses_df = pd.DataFrame({
    "Address ID": [1, 2, 3],
    "Address": ["Address 1", "Address 2", "Address 3"],
    "Latitude": [50.4501, 50.4547, 50.4591],
    "Longitude": [30.5234, 30.5238, 30.5297]
})

# Streamlit App
st.title("Territory Mapping with Named Polygons")

# Map Initialization
m = folium.Map(location=[addresses_df["Latitude"].mean(), addresses_df["Longitude"].mean()], zoom_start=12)

# Add markers for addresses
for _, row in addresses_df.iterrows():
    folium.Marker(location=[row["Latitude"], row["Longitude"]], popup=row["Address"]).add_to(m)

# Add drawing tools
draw = Draw(export=True)
draw.add_to(m)

# Display the map in Streamlit
st.write("Draw a polygon on the map, name it, and save.")
map_data = st_folium(m, width=700, height=500)

# Input for polygon name
polygon_name = st.text_input("Enter a name for the polygon:", "")

# Button to save the polygon with the name
if st.button("Save Polygon"):
    if map_data and "last_active_drawing" in map_data and map_data["last_active_drawing"]:
        # Get polygon coordinates
        polygon_coords = map_data["last_active_drawing"]["geometry"]["coordinates"][0]
        
        # Create Polygon object
        polygon = Polygon([(coord[1], coord[0]) for coord in polygon_coords])  # Flip coordinates
        
        # Store polygon name and coordinates
        st.session_state.setdefault("polygons", []).append({"name": polygon_name, "coordinates": polygon_coords})
        
        st.success(f"Polygon '{polygon_name}' saved successfully!")
    else:
        st.error("No polygon drawn. Please draw a polygon first.")

# Display saved polygons
if "polygons" in st.session_state:
    st.write("Saved Polygons:")
    for poly in st.session_state["polygons"]:
        st.write(f"Name: {poly['name']}, Coordinates: {poly['coordinates']}")
