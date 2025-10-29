import geopandas as gpd
import shapely.geometry as geom
import pyproj

# 1. Load water body shapefile (coastline + lakes/rivers). example: SWBD or NHD or downloaded OSM water layer.
water = gpd.read_file("water_shapefile.shp")

# 2. Load your points
import pandas as pd
df = pd.DataFrame({"lon": [...], "lat": [...]})
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")

# 3. Project to an appropriate local coordinate system for accurate metre distances
gdf = gdf.to_crs(epsg=3857)  # Web Mercator as example (units ~ metres, though some distortion)
water_proj = water.to_crs(epsg=3857)

# 4. Compute distance for each point: min distance to any water geometry
gdf["dist_to_water_m"] = gdf.geometry.apply(lambda pt: water_proj.distance(pt).min())

print(gdf)

