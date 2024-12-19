import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import pandas as pd
import json
import random

# Function to generate a random color in hexadecimal
def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Address dataset (replace this with your actual dataset)
addresses_df = pd.DataFrame({
    "Address ID": [1, 2, 3],
    "Address": ["Address 1", "Address 2", "Address 3"],
    "Latitude": [50.4501, 50.4547, 50.4591],
    "Longitude": [30.5234, 30.5238, 30.5297]
})

# Streamlit App
st.title("Territory Mapping with Automatic Polygon Coloring")

# Initialize map
m = folium.Map(location=[addresses_df["Latitude"].mean(), addresses_df["Longitude"].mean()], zoom_start=12)

# Add markers for addresses
for _, row in addresses_df.iterrows():
    folium.Marker(location=[row["Latitude"], row["Longitude"]], popup=row["Address"]).add_to(m)

# Add drawing tools to the map
draw = Draw(export=True)
draw.add_to(m)

# Display the map
st.write("Draw polygons on the map, name them, and automatically assign colors.")
map_data = st_folium(m, width=700, height=500)

# Initialize session state for polygons
if "polygons" not in st.session_state:
    st.session_state["polygons"] = []

# Input for polygon name
polygon_name = st.text_input("Enter a name for the polygon:", "")

# Button to save the polygon with the name and random color
if st.button("Save Polygon"):
    if map_data and "last_active_drawing" in map_data and map_data["last_active_drawing"]:
        # Get polygon coordinates
        polygon_geojson = map_data["last_active_drawing"]  # Get the GeoJSON for the polygon
        polygon_coords = polygon_geojson["geometry"]["coordinates"]

        # Validate polygon name
        if not polygon_name.strip():
            st.error("Please enter a valid name for the polygon.")
        else:
            # Assign a random color to the polygon
            color = random_color()

            # Add the name and color to the GeoJSON's properties
            polygon_geojson["properties"] = {"name": polygon_name, "color": color}

            # Save the polygon to the session state
            st.session_state["polygons"].append(polygon_geojson)
            st.success(f"Polygon '{polygon_name}' saved with color {color}!")

            # Add the polygon to the map with the color
            folium.GeoJson(
                polygon_geojson,
                style_function=lambda x: {
                    "fillColor": polygon_geojson["properties"]["color"],
                    "color": polygon_geojson["properties"]["color"],
                    "fillOpacity": 0.5,
                },
                name=polygon_name,
            ).add_to(m)
    else:
        st.error("No polygon drawn. Please draw a polygon first.")

# Display saved polygons
if st.session_state["polygons"]:
    st.write("Saved Polygons:")
    for poly in st.session_state["polygons"]:
        st.write(f"Name: {poly['properties']['name']}, Color: {poly['properties']['color']}")

# Export polygons as GeoJSON
if st.session_state["polygons"]:
    geojson_data = {
        "type": "FeatureCollection",
        "features": st.session_state["polygons"],
    }

    # Convert to JSON string
    geojson_str = json.dumps(geojson_data, indent=2)

    # Download button
    st.download_button(
        label="Download Polygons as GeoJSON",
        data=geojson_str,
        file_name="polygons.geojson",
        mime="application/geo+json",
    )
