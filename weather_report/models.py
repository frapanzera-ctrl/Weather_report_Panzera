"""Data models used in the weather report."""

from dataclasses import dataclass


# frozen=True: a City cannot be changed after it is created
@dataclass(frozen=True)
class City:
    """A city with its name and coordinates in decimal degrees."""

    # Fields: the dataclass writes __init__, __repr__ and __eq__ from them
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
     
    # Read like an attribute (city.slug), used to name the data files
    @property
    def slug(self) -> str:
        """Return the name in a form usable in file names (e.g. "milan")"""
        return self.name.lower().replace(" ", "_")
