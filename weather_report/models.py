"""Data models used in the weather report."""

from dataclasses import dataclass

@dataclass(frozen=True)
class City:
    """A city for which weather data is downloaded.
    
    Attributes
    ----------
    name : str
        Name of the city in english (e.g. "Milan").
    latitude : float
        Latitude in decimal degrees, between -90 and 90.
    longitude : float 
        Longitude in decimal degrees, between -180 and 180.       
     """

    # TYPE HINT: expected types 
    name: str
    latitude: float
    longitude: float

    # Fail fast: raise an error if the coordinates are invalid
    def __post_init__(self) -> None:
        """Checks that the coordinates are valid."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(
                f"Invalid latitude for {self.name}: {self.latitude}"
            )
        if not -180 <= self.longitude <= 180:
            raise ValueError(
                f"Invalid longitude for {self.name}: {self.longitude}"
            )
        
    # Will be useful for storage.py for file names    
    @property
    def slug(self) -> str:
        """Return the name in a form usable in file names (e.g. "milan")"""
        return self.name.lower().replace(" ", "_")
    