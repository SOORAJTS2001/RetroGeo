import asyncio
import random

from RetroGeo import GeoLocator


async def main():
    rev = GeoLocator()
    locations = []
    # locations = [((9.964498569974612, 76.25592213325532))]
    # result = await rev.getLocationFromCoordinates(locations)
    # print(result)
    for _ in range(10):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        locations.append((lon, lat))
    print(await rev.getLocationFromCoordinates(locations))
    locations = []
    for _ in range(10):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        locations.append((lon, lat))
    print(await rev.getLocationFromCoordinates(locations))
    locations = []
    for _ in range(10):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        locations.append((lon, lat))

    print(await rev.getLocationFromCoordinates(locations))

    locations = []
    for _ in range(10):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        locations.append((lon, lat))

    print(await rev.getLocationFromCoordinates(locations))


if __name__ == '__main__':
    # asyncio.run(reverse_geocode(9.964498569974612, 76.25592213325532))
    asyncio.run(main())
