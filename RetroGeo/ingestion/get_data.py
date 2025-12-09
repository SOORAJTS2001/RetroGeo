import requests
import sqlite3
from shapely.geometry import shape

DB_PATH = "../data.db"

adm3s = set()
adm2s = set()
lowest_levels = set()

conn = sqlite3.connect(DB_PATH)

# -------------------------------
# ✅ Step 1: Select lowest ADM per ISO
# -------------------------------

for data in requests.get(
    "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM3/"
).json():
    adm3s.add(data["boundaryISO"])
    lowest_levels.add(data["simplifiedGeometryGeoJSON"])

for data in requests.get(
    "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM2/"
).json():
    if data["boundaryISO"] not in adm3s:
        adm2s.add(data["boundaryISO"])
        lowest_levels.add(data["simplifiedGeometryGeoJSON"])

for data in requests.get(
    "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM1/"
).json():
    if data["boundaryISO"] not in adm2s and data["boundaryISO"] not in adm3s:
        lowest_levels.add(data["simplifiedGeometryGeoJSON"])


# -------------------------------
# ✅ Step 2: UPSERT function
# -------------------------------

def upsert_location_batch(records):
    if not records:
        return

    cur = conn.cursor()

    cur.executemany("""
        INSERT INTO location_data (name, shape_id, coordinates)
        VALUES (?, ?, ?)
        ON CONFLICT(name, shape_id)
        DO UPDATE SET coordinates = excluded.coordinates;
    """, records)

    conn.commit()


# -------------------------------
# ✅ Step 3: Download GeoJSON and Insert
# -------------------------------

for level_url in lowest_levels:
    geojson = requests.get(level_url).json()
    features = geojson.get("features", [])

    records = []   # ✅ IMPORTANT: reset per batch

    for feature in features:
        properties = feature.get("properties", {})
        geom = feature.get("geometry")

        if not geom:
            continue

        name = properties.get("shapeName")
        shape_id = properties.get("shapeID")

        if not name or not shape_id:
            continue

        # ✅ Convert GeoJSON → Shapely → Binary WKB
        polygon = shape(geom)

        # ✅ Optional but HIGHLY recommended
        polygon = polygon.simplify(0.005, preserve_topology=True)

        coordinates_blob = polygon.wkb

        records.append((name, shape_id, coordinates_blob))

    print(f"✅ Inserted batch from: {level_url}")
    upsert_location_batch(records)


conn.close()
print("✅ All boundaries inserted successfully.")
