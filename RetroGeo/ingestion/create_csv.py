import asyncio
import csv
import sqlite3

from shapely import wkb

from RetroGeo import GeoLocator, ThreadTypeEnum

rev = GeoLocator()

DB_PATH = "../data.db"
OUTPUT_CSV = "geo-boundaries.csv"
locations = []
metadata = {}


async def export_centroids_to_csv():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT name, shape_id, coordinates
        FROM location_data;
    """)

    rows = cur.fetchall()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "shape_id", "lat", "lon", "admin1", "admin2"])

        for name, shape_id, coordinates_blob in rows:
            polygon = wkb.loads(coordinates_blob)
            centroid = polygon.centroid
            metadata[(centroid.y,centroid.x)] = [name,shape_id]
            locations.append((centroid.y,centroid.x))
        result = await rev.query(locations, mode=ThreadTypeEnum.MULTI_PROCESS)
        for location,data in result.items():
            writer.writerow([
                metadata[location][0],
                metadata[location][1],
                location[1],  # longitude
                location[0],  # latitude
                data.admin1,
                data.admin2
            ])
            f.flush()


    conn.close()
    print(f"Centroids written to: {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(export_centroids_to_csv())
