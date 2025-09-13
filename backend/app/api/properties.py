from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas import PropertyResponse
from app.services.nl_to_sql import nl_to_sql_service

router = APIRouter()

@router.get("/", response_model=List[PropertyResponse])
async def get_properties(
    db: Session = Depends(get_db),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    city: Optional[str] = None
):
    """
    Get properties with optional filtering
    """
    query = """
    SELECT * FROM properties 
    WHERE is_active = true
    """
    params = {}
    
    if property_type:
        query += " AND property_type ILIKE :property_type"
        params["property_type"] = f"%{property_type}%"
    
    if min_price:
        query += " AND asking_price >= :min_price"
        params["min_price"] = min_price
    
    if max_price:
        query += " AND asking_price <= :max_price"
        params["max_price"] = max_price
    
    if city:
        query += " AND address_city ILIKE :city"
        params["city"] = f"%{city}%"
    
    query += " ORDER BY listing_date DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    result = db.execute(text(query), params)
    properties = result.fetchall()
    
    return nl_to_sql_service._convert_to_responses(properties)

@router.get("/types")
async def get_property_types(db: Session = Depends(get_db)):
    """
    Get all available property types
    """
    query = """
    SELECT DISTINCT property_type 
    FROM properties 
    WHERE is_active = true 
    ORDER BY property_type
    """
    result = db.execute(text(query))
    types = [row[0] for row in result.fetchall()]
    return {"property_types": types}

@router.get("/cities")
async def get_cities(db: Session = Depends(get_db)):
    """
    Get all available cities
    """
    query = """
    SELECT DISTINCT address_city 
    FROM properties 
    WHERE is_active = true AND address_city IS NOT NULL 
    ORDER BY address_city
    """
    result = db.execute(text(query))
    cities = [row[0] for row in result.fetchall()]
    return {"cities": cities}