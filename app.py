import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Polygon, Point
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopandas as gpd

# Set page title
st.title("Google My Maps-like Tool: Geocode, Draw, and Analyze Territories")

# Step 1: Upload Address File
uploaded_file = st.file_uploader("Upload your REPS BASE.xlsx file", type=["xlsx"])

if uploaded_file:
    # Load the data
    df = pd.read_excel(uploaded_file)
    st.write("Sample Data:")
    st.dataframe(df.head())

    # Step 2: Geocode Addresses
    @st.cache_data
    def geocode_addresses(dataframe, address_column="Address new"):
        """Geocode addresses to get latitude and longitude."""
        geolocator = Nominatim(user_agent="geoapi")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        dataframe["location"] = dataframe[address_column].apply(geocode)
        dataframe["latitude"] = dataframe["location"].apply(lambda loc: loc.latitude if loc else None)
        dataframe["longitude"] = dataframe["location"].apply(lambda loc: loc.longitude if loc else None)
        return dataframe

    with st.spinner("Geocoding addresses. This might take a while..."):
        df = geocode_addresses(df)
    st.success("Geocoding completed!")
    st.write("Data with Coordinates:")
    st.dataframe(df.head())

    # Step 3: Create a Map with Drawing Tools
    def create_map_with_drawing(data):
        """Create a map with markers and drawing tools."""
        m = folium.Map(location=[48.3794, 31.1656], zoom_start=6)  # Centered on Ukraine

        # Add markers for addresses
        for _, row in data.iterrows():
            if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=row["Address new"],
                ).add_to(m)

        # Add drawing tools (polygon, rectangle)
        draw = Draw(
            draw_options={
                "polyline": False,
                "circle": False,
                "rectangle": True,
                "polygon": True,
                "marker": False,
            },
            edit_options={"edit": True, "remove": True},
        )
        draw.add_to(m)
        return m

    # Display map
    map_obj = create_map_with_drawing(df)
    st.write("Draw your territories below:")
    output = st_folium(map_obj, width=700, height=500)

    # Step 4: Handle Drawn Shapes
    if output["all_drawings"]:
        st.write("Territories created:")
        drawn_territories = []
        for drawing in output["all_drawings"]:
            if drawing["geometry"]["type"] == "Polygon":
                polygon_coords = drawing["geometry"]["coordinates"][0]
                polygon = Polygon(polygon_coords)
                drawn_territories.append(polygon)
                st.write(f"Coordinates: {polygon_coords}")

        # Step 5: Match Addresses to Territories
        st.write("Matching addresses to territories...")
        gdf_addresses = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
        )
        gdf_territories = gpd.GeoDataFrame(
            {"geometry": drawn_territories}, crs="EPSG:4326"
        )

        # Find points within polygons
        for i, territory in gdf_territories.iterrows():
            points_in_territory = gdf_addresses[
                gdf_addresses.geometry.within(territory.geometry)
            ]
            st.write(f"Territory {i + 1}:")
            st.write(points_in_territory)

        # Option to export matched data
        if st.button("Download Territories with Addresses"):
            output_file = "addresses_in_territories.xlsx"
            with pd.ExcelWriter(output_file) as writer:
                for i, territory in gdf_territories.iterrows():
                    points_in_territory = gdf_addresses[
                        gdf_addresses.geometry.within(territory.geometry)
                    ]
                    points_in_territory.to_excel(
                        writer, sheet_name=f"Territory {i + 1}", index=False
                    )
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Territories with Addresses",
                    data=file,
                    file_name="addresses_in_territories.xlsx",
                )
