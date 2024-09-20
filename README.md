# RetroGeo - An Offline Reverse Geocoding Library

## Overview
Our reverse geocoding library is a high-performance, offline solution that processes geographical coordinates to retrieve full addresses, including country, state, and city. With pre-downloaded datasets and no need for online queries or API calls, this library excels in applications where internet connectivity is limited or unavailable.

## Key Features
- **Offline-capable**  
  Process massive geospatial datasets without relying on external dependencies.
  
- **High accuracy**  
  Leverage built-in data compression and storage optimizations to minimize disk space while maintaining high accuracy.
  
- **Large-scale operations**  
  Efficiently handle vast amounts of location data, making it ideal for:
  
  - **Geospatial analysis**  
    Perform rapid location lookup and analysis without external dependencies.
  
  - **Mobile applications**  
    Develop offline-capable mobile apps that can handle large geospatial datasets.
  
  - **Data processing pipelines**  
    Streamline your data processing pipeline with efficient reverse geocoding operations.

## Why Choose Our Library?
- **No API calls**  
  Avoid online queries and reliance on external services, ensuring your application's independence and security.
  
- **High performance**  
  Optimized for speed and accuracy, our library can handle massive datasets without sacrificing performance.
  
- **Easy integration**  
  Simple to incorporate into your existing projects, with minimal setup required.

## Get Started

### Installation
Install our library via pip:

```bash
pip install RetroGeo
```
## Example

### For Single Thread Execution (For a single coordinate pair)
```python
import asyncio

from RetroGeo import GeoLocator, ThreadTypeEnum


async def main():
    rev = GeoLocator()
    locations = [(9.964498569974612, 76.25592213325532)]
    result = await rev.getLocationFromCoordinates(locations, mode=ThreadTypeEnum.SINGLE_THREADED.value)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
```
### For Multithread Execution (List of coordinates pairs)
```python
import asyncio
import random

from RetroGeo import GeoLocator


async def main():
    rev = GeoLocator()
    locations = []
    for _ in range(10000):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        locations.append((lon, lat))
    results = await rev.getLocationFromCoordinates(locations)


if __name__ == '__main__':
    asyncio.run(main())
```

## Output
The Output would a dictionary with key as the given coordinates and the output as the `LocationBaseModel`.
Which is a pydantic base model
```python
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
```

```markdown
{(9.964498569974612, 76.25592213325532): LocationBaseModel(lat=9.93988, lon=76.26022, name='Cochin', admin1='India', admin2='Kerala', admin1_id=101, admin2_id=4028, admin1_lat=20.0, admin1_lon=77.0, admin2_lat=10.8505159, admin2_lon=76.2710833)}
```
