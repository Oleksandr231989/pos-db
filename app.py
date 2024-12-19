import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Set page title
st.title("Custom Territory Mapping Tool")

# Step 1: Load the dataset
@st.cache_data
def load_data(file_path):
    """Loads the Excel file and returns a DataFrame."""
    return pd.read_excel(file_path)

uploaded_file = st.file_uploader("Upload your REPS BASE.xlsx file", type=["xlsx"])

if uploaded_file:
    base = load_data(uploaded_file)

    # Step 2: Geocode addresses
    @st.cache_data
    def geocode_addresses(dataframe):
        """Geocode addresses to get their latitude and longitude."""
        geolocator = Nominatim(user_agent="geoapi")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        dataframe["location"] = dataframe["Address new"].apply(geocode)
        dataframe["latitude"] = dataframe["location"].apply(lambda loc: loc.latitude if loc else None)
        dataframe["longitude"] = dataframe["location"].apply(lambda loc: loc.longitude if loc else None)
        return dataframe

    with st.spinner("Geocoding addresses..."):
        geocoded_data = geocode_addresses(base)
        st.success("Geocoding completed!")
        st.write("Sample Data with Geocoding:")
        st.dataframe(geocoded_data.head())

    # Step 3: Create a map
    @st.cache_data
    def create_map(data):
        """Creates a Folium map with address markers."""
        m = folium.Map(location=[48.3794, 31.1656], zoom_start=6)  # Centered on Ukraine
        for _, row in data.iterrows():
            if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=row["Address new"],
                ).add_to(m)
        return m

    map_obj = create_map(geocoded_data)

    # Display map with drawing tools
    st.write("Draw your custom territories below:")
    output = st_folium(map_obj, width=700, height=500)

    # Step 4: Save and process drawn territories
    if output["all_drawings"]:
        st.write("You have drawn the following territories:")
        for drawing in output["all_drawings"]:
            if drawing["geometry"]["type"] == "Polygon":
                polygon_coords = drawing["geometry"]["coordinates"][0]
                polygon = Polygon(polygon_coords)
                st.write(f"Territory: {polygon}")

        st.write("Save your territories for further analysis.")

    # Step 5: Download geocoded data
    if st.button("Download Geocoded Data"):
        geocoded_data.to_csv("geocoded_data.csv", index=False)
        st.download_button(
            label="Download Geocoded Data",
            data=open("geocoded_data.csv", "rb"),
            file_name="geocoded_data.csv",
            mime="text/csv",
        )
