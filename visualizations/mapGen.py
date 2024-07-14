import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import GoogleTiles
import streamlit as st

def generateRuptureMap(coordinates, site_coordinate, ruptureDataframe):

    class EsriShadedRelief(GoogleTiles):
        # Customize this class to use the specific Esri shaded relief tile service
        def _image_url(self, tile):
            x, y, z = tile
            return f'http://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}'

    # Define the map projection
    proj = ccrs.PlateCarree()
    terrain = EsriShadedRelief()  # Now using shaded relief instead of plain terrain

    # Create figure with a GeoAxes in the desired projection
    fig, ax = plt.subplots(figsize=(11, 14), subplot_kw={'projection': proj},
                           dpi=300)  # Increased DPI for better resolution

    # Set map extent with a small buffer to avoid white zones at the edges
    # ax.set_extent([site_coordinate[1]-10.5, site_coordinate[0]-2, site_coordinate[1]+1, site_coordinate[0]+10.5]) # Adjust these values based on your data extent
    ax.add_image(terrain, 8)  # The second argument is the zoom level of the tile, adjust as needed

    # Add natural earth features to mask water
    ocean_10m = cfeature.NaturalEarthFeature('physical', 'ocean', '10m', edgecolor='face',
                                             facecolor=cfeature.COLORS['water'])
    ax.add_feature(ocean_10m, zorder=5)

    # Add natural features with Cartopy
    ax.add_feature(cfeature.LAND, linewidth=0.5)  # Adjust line width for better visibility
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=6)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)

    # Add gridlines with labels -- LAT AND LONG INFORMATION
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.05, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    # Fault Line
    for i in range(len(coordinates) - 1):
        x_values = [coordinates[i][0], coordinates[i + 1][0]]
        y_values = [coordinates[i][1], coordinates[i + 1][1]]
        ax.plot(x_values, y_values, color='r', linewidth=0.9, label='Line Source', zorder=7)

    # Site Location
    ax.scatter(site_coordinate[0], site_coordinate[1], marker='^', color='y', edgecolor='black', linewidth=1.5, label='Site', s=100, zorder=7)

    # Site Location
    selected_id = st.selectbox("Select magnitude", ruptureDataframe["Magnitude"].unique())

    # Filter DataFrame based on selected ID
    filtered_df = ruptureDataframe[ruptureDataframe["Magnitude"] == selected_id]

    # Add lines to the map
    for _, row in filtered_df.iterrows():
        start = row["Starting coordinate"]
        end = row["Ending coordinate"]
        x_values = [start[0], end[0]]
        y_values = [start[1], end[1]]
        ax.plot(x_values, y_values, color='k', zorder=7)

    #
    ax.set_title('Ruptures and Site')
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_xlim([site_coordinate[0]-3, site_coordinate[0]+3])
    ax.set_ylim([site_coordinate[1]-2.5, site_coordinate[1]+2.5])

    return fig


