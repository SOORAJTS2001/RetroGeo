""" A Fast, Offline Reverse Geocoder in Python

A Python library for offline reverse geocoding. It improves on an existing library
called reverse_geocode developed by Richard Penman.
"""
import csv
import sys
import sqlite3
from pydantic import BaseModel, Field
from shapely import wkb
from thread_type import ThreadTypeEnum
from shapely.geometry import Point
import numpy as np
if sys.platform == 'win32':
    # Windows C long is 32 bits, and the Python int is too large to fit inside.
    # Use the limit appropriate for a 32-bit integer as the max file size
    csv.field_size_limit(2 ** 31 - 1)
else:
    csv.field_size_limit(sys.maxsize)
from scipy.spatial import cKDTree
from . import KD_Tree
# Schema of the cities file created by this library
RG_COLUMNS = ['name', 'shape_id', 'lat', 'lon', 'admin1', 'admin2']
FILENAME = "geo-boundaries.csv"
# WGS-84 major axis in kms
A = 6378.137

# WGS-84 eccentricity squared
E2 = 0.00669437999014
DB_PATH = "data.db"
DEFAULT_K = 3

class LocationBaseModel(BaseModel):
    lat: float = Field(..., description="Latitude of the main location")
    lon: float = Field(..., description="Longitude of the main location")
    name: str = Field(..., description="Name of the location")
    admin1: str = Field(..., description="Name of the primary administrative division (e.g., country)")
    admin2: str = Field(..., description="Name of the secondary administrative division (e.g., state or province)")


def singleton(cls):
    """
    Function to get single instance of the RGeocoder class
    """
    instances = {}

    def getinstance(**kwargs):
        """
        Creates a new RGeocoder instance if not created already
        """
        if cls not in instances:
            instances[cls] = cls(**kwargs)
        return instances[cls]

    return getinstance


@singleton
class RGeocoder(object):
    """
    The main reverse geocoder class
    """

    def __init__(self, mode: ThreadTypeEnum, verbose=True):
        """ Class Instantiation
        Args:
        mode (int): Library supports the following two modes:
                    - 1 = Single-threaded K-D Tree
                    - 2 = Multi-threaded K-D Tree (Default)
        verbose (bool): For verbose output, set to True
        stream (io.StringIO): An in-memory stream of a custom data source
        """
        self.mode = mode
        self.verbose = verbose
        coordinates, self.locations = self.load()
        self.conn = sqlite3.connect(DB_PATH)
        self.curr = self.conn.cursor()
        if mode == ThreadTypeEnum.SINGLE_PROCESS:  # Single-process
            self.tree = cKDTree(coordinates)
        else:  # Multi-process
            self.tree = KD_Tree.cKDTree_MP(coordinates)

    def safe_load(self,blob):
        geom = wkb.loads(blob)
        return geom[0] if isinstance(geom, np.ndarray) else geom

    def query_shape(self, filters: list[tuple[str, str]]) -> list:
        if not filters:
            return []

        placeholders = ",".join(["(?, ?)"] * len(filters))

        query = f"""
            SELECT name, shape_id, coordinates
            FROM location_data
            WHERE (name, shape_id) IN ({placeholders});
        """

        flat_params = [item for pair in filters for item in pair]

        self.curr.execute(query, flat_params)
        rows = self.curr.fetchall()

        lookup = {
            (name, shape_id): self.safe_load(blob)
            for name, shape_id, blob in rows
        }

        return [lookup.get(pair) for pair in filters]

    def geo_contains(self,search_location:[float,float],indexes:list[int]):
        search_location = Point(*search_location)
        filters = [(self.locations[index].get("name"),self.locations[index].get("shape_id")) for index in indexes]
        for index,geometry in zip(indexes,self.query_shape(filters)):
            if geometry.contains(search_location):
                return self.locations[index]



    def query(self, coordinates):
        """
        Function to query the K-D tree to find the nearest city
        Args:
        coordinates (list): List of tuple coordinates, i.e. [(latitude, longitude)]
        """
        if self.mode == ThreadTypeEnum.SINGLE_PROCESS:
            _, indices = self.tree.query(coordinates, k=DEFAULT_K)
        else:
            _, indices = self.tree.pquery(coordinates, k=DEFAULT_K)
        return [self.geo_contains(coordinates[position],indexes_) for position,indexes_ in enumerate(indices)]

    def load(self):
        """
        Function that loads a custom data source
        Args:
        stream (io.StringIO): An in-memory stream of a custom data source.
                              The format of the stream must be a comma-separated file
                              with header containing the columns defined in RG_COLUMNS.
        """
        with open(FILENAME, mode='r', newline='') as file:
            stream_reader = csv.DictReader(file)
            header = stream_reader.fieldnames
            if header != RG_COLUMNS:
                raise csv.Error('Input must be a comma-separated file with header containing ' + \
                                'the following columns - %s. For more help, visit: ' % (','.join(RG_COLUMNS)) + \
                                'https://github.com/thampiman/reverse-geocoder')

            # Load all the coordinates and locations
            geo_coords, locations = [], []
            for row in stream_reader:
                geo_coords.append((row['lat'], row['lon']))
                locations.append(row)
            return geo_coords, locations


def search(geo_coords, mode, verbose=False):
    """
    Function to query for a list of coordinates
    """
    if not isinstance(geo_coords, tuple) and not isinstance(geo_coords, list):
        raise TypeError('Expecting a tuple or a tuple/list of tuples')
    elif not isinstance(geo_coords[0], tuple):
        geo_coords = [geo_coords]
    _rg = RGeocoder(mode=mode, verbose=verbose)
    return dict(zip(geo_coords, [LocationBaseModel(**result) for result in _rg.query(geo_coords) if result]))
