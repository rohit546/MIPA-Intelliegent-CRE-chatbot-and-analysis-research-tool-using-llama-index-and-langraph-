"""
FastAPI Backend for Georgia Properties React App
Provides REST API endpoints for the chatbot and property gallery
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.dirname(__file__))

from enhanced_sql_integration import EnhancedSQLGenerator
from config import DATABASE_URL, OPENAI_API_KEY

app = FastAPI(title="Georgia Properties API", version="1.0.0")

# Enable CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced SQL generator
enhanced_generator = EnhancedSQLGenerator(DATABASE_URL, OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sql_query: Optional[str] = None
    properties: List[dict] = []
    validation_status: str = "success"
    was_corrected: bool = False
    correction_explanation: Optional[str] = None

class Property(BaseModel):
    id: int
    name: str
    price: float
    size_acres: Optional[float] = None
    property_type: Optional[str] = None
    address: dict
    listing_url: Optional[str] = None
    zoning: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_count: int
    limit: int
    has_next: bool
    has_prev: bool

class PropertiesResponse(BaseModel):
    properties: List[Property]
    pagination: PaginationInfo

@app.get("/")
async def root():
    return {"message": "Georgia Properties API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - processes natural language queries
    """
    try:
        user_query = request.message.strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # Check for simple greetings
        if user_query.lower() in ["hello", "hi", "hey", "help"]:
            return ChatResponse(
                response="Hi! I can help you find commercial properties in Georgia. Try asking about gas stations, retail properties, or specific locations like 'properties in Walton County'.",
                properties=[]
            )
        
        # Process query through enhanced pipeline
        from app_enhanced import setup_enhanced_query_engine, enhanced_query_with_feedback
        
        # Setup query engine
        query_engine, enhanced_generator, engine = setup_enhanced_query_engine(DATABASE_URL, OPENAI_API_KEY)
        
        # Process query
        response = enhanced_query_with_feedback(user_query, query_engine, enhanced_generator, engine)
        
        # Extract results
        properties = []
        sql_query = None
        validation_status = "success"
        was_corrected = False
        correction_explanation = None
        
        if hasattr(response, 'metadata'):
            metadata = response.metadata
            sql_query = metadata.get('enhanced_sql') or metadata.get('sql_query')
            validation_status = metadata.get('validation_status', 'success')
            was_corrected = metadata.get('was_corrected', False)
            correction_explanation = metadata.get('correction_explanation')
            
            # Parse results into structured format
            if 'result' in metadata and metadata['result']:
                properties = parse_query_results(metadata['result'])
        
        # Generate response text
        if properties:
            response_text = f"Found {len(properties)} properties matching your search."
            if was_corrected:
                response_text += f" (Query was automatically optimized: {correction_explanation})"
        else:
            response_text = "No properties found matching your criteria. Try adjusting your search parameters."
        
        return ChatResponse(
            response=response_text,
            sql_query=sql_query,
            properties=properties,
            validation_status=validation_status,
            was_corrected=was_corrected,
            correction_explanation=correction_explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/properties", response_model=PropertiesResponse)
async def get_properties(
    page: int = 1, 
    limit: int = 20,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None
):
    """
    Get properties for the gallery with pagination and filtering
    """
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        
        # Build WHERE clause based on filters
        where_conditions = ["asking_price IS NOT NULL"]
        params = {"limit": limit, "offset": offset}
        
        if property_type:
            where_conditions.append("(property_type ILIKE :property_type OR property_subtype ILIKE :property_type)")
            params["property_type"] = f"%{property_type}%"
            
        if min_price is not None:
            where_conditions.append("asking_price >= :min_price")
            params["min_price"] = min_price
            
        if max_price is not None:
            where_conditions.append("asking_price <= :max_price")
            params["max_price"] = max_price
            
        if search:
            where_conditions.append("(name ILIKE :search OR description ILIKE :search OR address->>'city' ILIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = " AND ".join(where_conditions)
        
        with engine.connect() as conn:
            # Get total count
            count_query = f"""
                SELECT COUNT(*) 
                FROM "Georgia Properties" 
                WHERE {where_clause}
            """
            count_result = conn.execute(text(count_query), params)
            total_count = count_result.scalar()
            
            # Get properties for current page
            properties_query = f"""
                SELECT id, name, property_type, property_subtype, asking_price, 
                       address, thumbnail_url, size_acres, description, status,
                       listing_url, zoning
                FROM "Georgia Properties" 
                WHERE {where_clause}
                ORDER BY asking_price DESC 
                LIMIT :limit OFFSET :offset
            """
            result = conn.execute(text(properties_query), params)
            
            properties = []
            for row in result.fetchall():
                try:
                    # Parse address if it's JSON
                    address = row[5]
                    if isinstance(address, str) and address.startswith('{'):
                        address = json.loads(address.replace("'", '"'))
                    elif not isinstance(address, dict):
                        address = {"fullAddress": str(address)} if address else {}
                    
                    # Format property type
                    prop_type = row[2] or row[3] or "Unknown"
                    
                    properties.append({
                        "id": row[0],
                        "name": row[1] or "Unnamed Property",
                        "price": float(row[4]) if row[4] else 0,
                        "size_acres": float(row[7]) if row[7] else None,
                        "property_type": prop_type,
                        "address": address,
                        "listing_url": row[10],
                        "zoning": row[11],
                        "thumbnail_url": row[6],
                        "description": row[8],
                        "status": row[9]
                    })
                except Exception as e:
                    continue
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit  # Ceiling division
            has_next = page < total_pages
            has_prev = page > 1
            
            return {
                "properties": properties,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "limit": limit,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching properties: {str(e)}")

def parse_query_results(results):
    """Parse SQL query results into structured property objects"""
    properties = []
    
    for row in results:
        try:
            property_data = {
                "id": row[0] if len(row) > 0 and row[0] else 0,
                "name": row[1] if len(row) > 1 and row[1] else "Unnamed Property",
                "price": 0,
                "size_acres": None,
                "property_type": None,
                "address": {},
                "listing_url": None,
                "zoning": None
            }
            
            # Parse columns dynamically
            for i, value in enumerate(row[2:], start=2):
                if value is None:
                    continue
                
                if isinstance(value, (int, float)):
                    if value >= 1000:  # Likely price
                        property_data["price"] = float(value)
                    elif 0.01 <= value <= 1000:  # Likely acres
                        property_data["size_acres"] = float(value)
                elif isinstance(value, str):
                    if value.startswith('https://www.crexi.com'):
                        property_data["listing_url"] = value
                    elif '{' in value and ('street' in value.lower() or 'city' in value.lower()):
                        try:
                            property_data["address"] = json.loads(value.replace("'", '"'))
                        except:
                            property_data["address"] = {"fullAddress": value}
                    elif any(word in value.lower() for word in ['retail', 'gas', 'restaurant', 'land']):
                        if not property_data["property_type"]:
                            property_data["property_type"] = value
                    elif any(word in value.lower() for word in ['commercial', 'residential', 'industrial']):
                        property_data["zoning"] = value
            
            properties.append(property_data)
            
        except Exception as e:
            continue
    
    return properties

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)