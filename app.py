import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Polygon, Point
import geopandas as gpd

# Set page title
st.title("Google My Maps-like Tool: Draw and Analyze Territories")

# Step 1: Upload Address File
uploaded_file = st.file_uploader("Upload your REPS BASE.xlsx file", type=["xlsx"])

if uploaded_file:
    # Load the data
    df = pd.read_excel(uploaded_file)
    st.write("Sample Data:")
    st.dataframe(df.head())

    # Ensure geocoded latitude and longitude columns
    if "latitude" not in df.columns or "longitude" not in df.columns:
        st.error("The file must contain 'latitude' and 'longitude' columns.")
    else:
        # Step 2: Create a Map with Drawing Tools
        def create_map(data):
            """Create a map with markers and drawing tools."""
            m = folium.Map(location=[48.3794, 31.1656], zoom_start=6)  # Centered on Ukraine

            # Add markers for addresses
            for _, row in data.iterrows():
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=row["Address new"] if "Address new" in row else "Address",
                ).add_to(m)

            # Add drawing tools (polygon, rectangle, marker)
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
        map_obj = create_map(df)
        st.write("Draw your territories below:")
        output = st_folium(map_obj, width=700, height=500)

        # Step 3: Analyze Drawn Shapes
        if output["all_drawings"]:
            st.write("Territories created:")
            drawn_territories = []
            for drawing in output["all_drawings"]:
                if drawing["geometry"]["type"] == "Polygon":
                    polygon_coords = drawing["geometry"]["coordinates"][0]
                    polygon = Polygon(polygon_coords)
                    drawn_territories.append(polygon)
                    st.write(f"Coordinates: {polygon_coords}")

            # Step 4: Match Addresses to Territories
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
