from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class PropertyAddress(BaseModel):
    street: Optional[str] = None
    city: str
    state: str = "Georgia"
    zip_code: Optional[str] = None
    county: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    @property
    def full_address(self) -> str:
        parts = []
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        return ", ".join(parts)

class PropertyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    property_type: str
    property_subtype: Optional[str] = None
    
    # Address
    address: PropertyAddress
    
    # Pricing
    asking_price: Optional[float] = None
    price_per_sqft: Optional[float] = None
    
    # Size
    size_sqft: Optional[float] = None
    size_acres: Optional[float] = None
    lot_size_sqft: Optional[float] = None
    
    # Details
    year_built: Optional[int] = None
    zoning: Optional[str] = None
    
    # Listing
    listing_date: datetime
    listing_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    id: str
    content: str
    type: str  # 'user' | 'assistant' | 'error'
    timestamp: datetime
    properties: Optional[List[PropertyResponse]] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    message: ChatMessage
    sql_query: Optional[str] = None
    execution_time: Optional[float] = None