import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from shapely.geometry import Polygon
import json

# Streamlit App
st.title("Territory Mapping with Named Polygons and GeoJSON Export")

# Initialize map
m = folium.Map(location=[50.4501, 30.5234], zoom_start=12)

# Add drawing tools to the map
draw = Draw(export=True)
draw.add_to(m)

# Display the map
st.write("Draw polygons on the map, name them, and export as GeoJSON.")
map_data = st_folium(m, width=700, height=500)

# Initialize session state for polygons
if "polygons" not in st.session_state:
    st.session_state["polygons"] = []

# Input for polygon name
polygon_name = st.text_input("Enter a name for the polygon:", "")

# Button to save the polygon with the name
if st.button("Save Polygon"):
    if map_data and "last_active_drawing" in map_data and map_data["last_active_drawing"]:
        # Get polygon coordinates
        polygon_geojson = map_data["last_active_drawing"]  # Get the GeoJSON for the polygon
        polygon_coords = polygon_geojson["geometry"]["coordinates"]
        
        # Validate polygon name
        if not polygon_name.strip():
            st.error("Please enter a valid name for the polygon.")
        else:
            # Add the name to the GeoJSON's properties
            polygon_geojson["properties"] = {"name": polygon_name}

            # Save the polygon to the session state
            st.session_state["polygons"].append(polygon_geojson)
            st.success(f"Polygon '{polygon_name}' saved successfully!")
    else:
        st.error("No polygon drawn. Please draw a polygon first.")

# Display saved polygons
if st.session_state["polygons"]:
    st.write("Saved Polygons:")
    for poly in st.session_state["polygons"]:
        st.write(f"Name: {poly['properties']['name']}, Coordinates: {poly['geometry']['coordinates']}")

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
