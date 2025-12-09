import asyncio
import random
from pytictoc import TicToc
from RetroGeo import GeoLocator, ThreadTypeEnum
from rgeocoder import ReverseGeocoder
rg = ReverseGeocoder()

async def main():
    t = TicToc()
    rev = GeoLocator()
    locations = [(-73.2404,43.2342)]
    result = await rev.query(locations,mode=ThreadTypeEnum.MULTI_PROCESS)
    print(result)

    r = rg.nearest(43.2342, -73.2404)
    print("Rust reverse")
    print(r.admin1)
    print(r.admin2)
    # locations = [
    #     (77.5946, 12.9716),  # Bengaluru, Karnataka, India
    #     (72.8777, 19.0760),  # Mumbai, Maharashtra, India
    #     (88.3639, 22.5726),  # Kolkata, West Bengal, India
    #     (80.2707, 13.0827),  # Chennai, Tamil Nadu, India
    #     (77.1025, 28.7041),  # New Delhi, India
    #
    #     (-74.0060, 40.7128),  # New York City, USA
    #     (-118.2437, 34.0522),  # Los Angeles, USA
    #     (-87.6298, 41.8781),  # Chicago, USA
    #     (-122.4194, 37.7749),  # San Francisco, USA
    #     (-95.3698, 29.7604),  # Houston, USA
    #
    #     (139.6917, 35.6895),  # Tokyo, Japan
    #     (116.4074, 39.9042),  # Beijing, China
    #     (121.4737, 31.2304),  # Shanghai, China
    #     (126.9780, 37.5665),  # Seoul, South Korea
    #     (103.8198, 1.3521),  # Singapore
    #
    #     (2.3522, 48.8566),  # Paris, France
    #     (-0.1276, 51.5072),  # London, United Kingdom
    #     (13.4050, 52.5200),  # Berlin, Germany
    #     (151.2093, -33.8688),  # Sydney, Australia
    #     (-58.3816, -34.6037)  # Buenos Aires, Argentina
    # ]
    # print(await rev.getLocationFromCoordinates(locations,mode=ThreadTypeEnum.MULTI_THREADED))
    # locations = []
    # for _ in range(1000000):
    #     lat = random.uniform(-90, 90)
    #     lon = random.uniform(-180, 180)
    #     locations.append((lon, lat))
    # t.tic()
    # await rev.query(locations, mode=ThreadTypeEnum.MULTI_PROCESS)
    # t.toc()


if __name__ == '__main__':
    # asyncio.run(reverse_geocode(9.964498569974612, 76.25592213325532))
    asyncio.run(main())
