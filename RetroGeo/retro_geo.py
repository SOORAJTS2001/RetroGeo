""" A Fast, Offline Reverse Geocoder in Python

A Python library for offline reverse geocoding. It improves on an existing library
called reverse_geocode developed by Richard Penman.
"""
import csv
import sys
from typing import Optional

from pydantic import BaseModel, Field

from .thread_type import ThreadTypeEnum

if sys.platform == 'win32':
    # Windows C long is 32 bits, and the Python int is too large to fit inside.
    # Use the limit appropriate for a 32-bit integer as the max file size
    csv.field_size_limit(2 ** 31 - 1)
else:
    csv.field_size_limit(sys.maxsize)
from scipy.spatial import cKDTree
from . import KD_Tree
# Schema of the cities file created by this library
RG_COLUMNS = ['lat', 'lon', 'name', 'admin1', 'admin2', 'admin1_id', 'admin2_id', 'admin1_lat', 'admin1_lon',
              'admin2_lat', 'admin2_lon']
FILENAME = "cities.csv"
# WGS-84 major axis in kms
A = 6378.137

# WGS-84 eccentricity squared
E2 = 0.00669437999014


class LocationBaseModel(BaseModel):
    lat: float = Field(..., description="Latitude of the main location")
    lon: float = Field(..., description="Longitude of the main location")
    name: str = Field(..., description="Name of the location")
    admin1: str = Field(..., description="Name of the primary administrative division (e.g., country)")
    admin2: str = Field(..., description="Name of the secondary administrative division (e.g., state or province)")
    admin1_id: int = Field(..., description="ID of the primary administrative division")
    admin2_id: int = Field(..., description="ID of the secondary administrative division")
    admin1_lat: Optional[float] = Field(None, description="Latitude of the primary administrative division")
    admin1_lon: Optional[float] = Field(None, description="Longitude of the primary administrative division")
    admin2_lat: Optional[float] = Field(None, description="Latitude of the secondary administrative division")
    admin2_lon: Optional[float] = Field(None, description="Longitude of the secondary administrative division")


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
        if mode == ThreadTypeEnum.SINGLE_THREADED:  # Single-process
            self.tree = cKDTree(coordinates)
        else:  # Multi-process
            self.tree = KD_Tree.cKDTree_MP(coordinates)

    def query(self, coordinates):
        """
        Function to query the K-D tree to find the nearest city
        Args:
        coordinates (list): List of tuple coordinates, i.e. [(latitude, longitude)]
        """
        if self.mode == 1:
            _, indices = self.tree.query(coordinates, k=1)
        else:
            _, indices = self.tree.pquery(coordinates, k=1)
        len_ = len(self.locations)
        return [self.locations[index] for index in indices if index<len_]

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
    return dict(zip(geo_coords,[LocationBaseModel(**result) for result in _rg.query(geo_coords)]))
