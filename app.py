import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
import json

# Streamlit App
st.title("Territory Mapping with GeoJSON Export")

# Initialize map
m = folium.Map(location=[50.4501, 30.5234], zoom_start=12)

# Add drawing tools to the map
draw = Draw(export=True)
draw.add_to(m)

# Display the map
st.write("Draw polygons on the map and export them as GeoJSON.")
map_data = st_folium(m, width=700, height=500)

# Initialize session state for polygons
if "polygons" not in st.session_state:
    st.session_state["polygons"] = []

# Save the polygon if a new one is drawn
if map_data and "last_active_drawing" in map_data and map_data["last_active_drawing"]:
    st.write("Polygon Coordinates:", map_data["last_active_drawing"]["geometry"]["coordinates"])
    polygon_geojson = map_data["last_active_drawing"]  # Get the GeoJSON for the polygon
    st.session_state["polygons"].append(polygon_geojson)

# Export polygons as GeoJSON
if st.session_state["polygons"]:
    st.write("Saved Polygons:")
    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": poly["geometry"], "properties": {}} for poly in st.session_state["polygons"]
        ],
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
