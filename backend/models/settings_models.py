from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Coordinates(BaseModel):
    minLat: float
    maxLat: float
    minLon: float
    maxLon: float

class Area(BaseModel):
    areaId: str
    enabled: bool
    coordinates: Coordinates
    presetArea: str

class ChatGIS(BaseModel):
    salutation: str
    enableAreasOfInterest: bool
    areas: List[Area]

class GeoRAG(BaseModel):
    selectedModel: str
    enableAreasOfInterest: bool
    areas: List[Area]

class Metadata(BaseModel):
    createdAt: datetime
    updatedAt: datetime
    version: str

class UserSettings(BaseModel):
    userId: int
    settingsType: str = "user_settings"
    chatGIS: ChatGIS
    geoRAG: GeoRAG
    metadata: Metadata

class SettingsResponse(BaseModel):
    success: bool
    message: str
    settings: Optional[UserSettings] = None
