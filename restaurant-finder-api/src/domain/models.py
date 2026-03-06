"""Domain models for restaurant data."""
from typing import Optional, List
from pydantic import BaseModel, Field
class Restaurant(BaseModel):
    """Restaurant model with expanded fields."""
    
    name: str = Field(description="Restaurant name")
    cuisine: Optional[str] = Field(None, description="Type of cuisine")
    location: Optional[str] = Field(None, description="Location/address")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating 0-5")
    price_level: Optional[str] = Field(None, description="Price level $-$$$$")
    phone: Optional[str] = Field(None, description="Phone number")
    
class SearchResult(BaseModel):
    """Search results container."""

    query: str = Field(description="Original Search query")
    restaurants: List[Restaurant] = Field(default_factory=list)
    total_results: int = Field(default=0)
