from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    property_type = Column(String, nullable=False)
    property_subtype = Column(String)
    
    # Location
    address_street = Column(String)
    address_city = Column(String)
    address_state = Column(String, default="Georgia")
    address_zip = Column(String)
    address_county = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Pricing
    asking_price = Column(Float)
    price_per_sqft = Column(Float)
    
    # Size
    size_sqft = Column(Float)
    size_acres = Column(Float)
    lot_size_sqft = Column(Float)
    
    # Property details
    year_built = Column(Integer)
    zoning = Column(String)
    
    # Listing info
    listing_date = Column(DateTime, default=datetime.utcnow)
    listing_url = Column(String)
    thumbnail_url = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_query = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    execution_success = Column(Boolean, nullable=False)
    result_count = Column(Integer)
    error_message = Column(Text)
    feedback_score = Column(Integer)  # 1-5 rating
    
    created_at = Column(DateTime, default=datetime.utcnow)