import sqlite3

conn = sqlite3.connect("../data.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS location_data (
    name TEXT NOT NULL,
    shape_id TEXT NOT NULL,
    coordinates BLOB NOT NULL,
    PRIMARY KEY (name, shape_id)
);
""")

conn.commit()
conn.close()
