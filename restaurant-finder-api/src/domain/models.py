"""Domain models for restaurant data."""
from typing import Optional
from pydantic import BaseModel, Field

class Restaurant(BaseModel): 
    """Restaurant model - MVP version."""
    
    name: str = Field(description="Restaurant name")
    cuisine: Optional[str] = Field(None, description="Type of cuisine")
    location: Optional[str] = Field(None, description="Location/address")

    