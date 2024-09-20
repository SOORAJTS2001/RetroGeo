import asyncio
import csv
import os
from io import StringIO

import httpx
import pandas as pd
from aiocache import cached
from aiocache.serializers import PickleSerializer

from RetroGeo.thread_type import ThreadTypeEnum
from RetroGeo.retro_geo import search

STATES_URL = f"https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/states.csv"
COUNTRIES_URL = f"https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/countries.csv"
CITIES_URL = f"https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/cities.csv"
FILENAME = "cities.csv"


class GeoLocator:
    def __init__(self):
        self.countries = {}
        self.states = {}

    async def _load_countries_states(self, url: str):
        if not self.countries or not self.states:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response = response.text
                csv_reader = csv.DictReader(response.splitlines())
                for row in csv_reader:
                    if row['latitude'] and row['longitude']:
                        id = int(row['id'])  # Adjust this key based on your CSV structure
                        latitude = float(row['latitude'])  # Adjust this key based on your CSV structure
                        longitude = float(row['longitude'])  # Adjust this key based on your CSV structure
                        if url == STATES_URL:
                            self.states[id] = (latitude, longitude)
                        elif url == COUNTRIES_URL:
                            self.countries[id] = (latitude, longitude)

    @cached(ttl=3600, serializer=PickleSerializer())
    async def _load_csv(self, filepath_or_buffer):
        return pd.read_csv(filepath_or_buffer)

    async def _load_cities(self):
        if not os.path.exists(FILENAME):
            await asyncio.gather(*[self._load_countries_states(url) for url in [STATES_URL, COUNTRIES_URL]])
            async with httpx.AsyncClient() as client:
                response = await client.get(CITIES_URL)
                response.raise_for_status()  # Ensure we handle errors if the request fails
                self.df = await self._load_csv(StringIO(response.text))
                df = self.df.rename(columns={
                    'latitude': 'lat',
                    'longitude': 'lon',
                    'state_id': 'admin2_id',
                    'state_name': 'admin2',
                    'country_id': 'admin1_id',
                    'country_name': 'admin1'
                })
                df = df[['lat', 'lon', 'name', 'admin1', 'admin2', 'admin1_id', 'admin2_id']]
                df['admin1_lat'] = df['admin1_id'].apply(lambda x: self.countries.get(x, (None, None))[0])
                df['admin1_lon'] = df['admin1_id'].apply(lambda x: self.countries.get(x, (None, None))[1])
                df['admin2_lat'] = df['admin2_id'].apply(lambda x: self.states.get(x, (None, None))[0])
                df['admin2_lon'] = df['admin2_id'].apply(lambda x: self.states.get(x, (None, None))[1])
                self.df = df.dropna(subset=['admin1_lat', 'admin1_lon', 'admin2_lat', 'admin2_lon'])
                self.df.to_csv(FILENAME, index=False)

    async def getLocationFromCoordinates(self, locations: list,
                                         mode: ThreadTypeEnum = ThreadTypeEnum.MULTI_THREADED.value):
        await self._load_cities()
        return search(locations, mode=mode)
