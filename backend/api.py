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
from smarty_address_analyzer_new import SmartyAddressAnalyzer

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

# Initialize Smarty address analyzer
smarty_analyzer = SmartyAddressAnalyzer(
    auth_id="b5635821-7595-0e7d-5899-15d9c637aa83",
    auth_token="1G3Z5qylilfg9aR2bhd0"
)

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
    asking_price: float
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

class AddressRequest(BaseModel):
    address: str

class AddressAnalysisResponse(BaseModel):
    formatted_address: str
    city: str
    state: str
    zip_code: str
    county: Optional[str] = None
    property_info: Optional[dict] = None
    financial_info: Optional[dict] = None
    risk_analysis: Optional[dict] = None
    investment_analysis: Optional[dict] = None

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
        
        # Process query through enhanced SQL generation
        # First parse the query to get structured filters
        parsed_query = enhanced_generator.query_parser.parse(user_query)
        # Generate SQL query from parsed query
        gpt4_query = enhanced_generator.sql_generator.generate(parsed_query)
        
        # Use enhanced generator to validate and execute
        result = enhanced_generator.generate_and_validate_sql(user_query, gpt4_query)
        
        # Extract results
        properties = []
        sql_query = result.get('final_sql')
        validation_status = result.get('validation_status', 'success')
        was_corrected = result.get('was_corrected', False)
        correction_explanation = result.get('correction_explanation')
        
        # Get the SQL results and convert to complete property details
        if result.get('results') and hasattr(result['results'], 'rows') and len(result['results'].rows) > 0:
            properties = fetch_complete_property_details(result['results'].rows)
        
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
                        "asking_price": float(row[4]) if row[4] else 0,
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

@app.post("/address-analysis", response_model=AddressAnalysisResponse)
async def analyze_address(request: AddressRequest):
    """
    Analyze address using Smarty US Address Enrichment API
    """
    try:
        address = request.address.strip()
        
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
        # Analyze address using Smarty API
        result = smarty_analyzer.analyze_address(address)
        
        if not result:
            raise HTTPException(status_code=404, detail="Address not found or invalid")
        
        return AddressAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing address: {str(e)}")

def fetch_complete_property_details(results):
    """Fetch complete property details from database using IDs from SQL query results"""
    from sqlalchemy import create_engine, text
    
    if not results:
        return []
    
    try:
        engine = create_engine(DATABASE_URL)
        property_ids = []
        
        # Extract property IDs from query results
        for row in results:
            if len(row) > 0 and row[0]:
                property_ids.append(row[0])
        
        if not property_ids:
            return []
        
        # Fetch complete property details for these IDs
        id_list = ','.join(map(str, property_ids))
        detailed_query = text(f"""
            SELECT 
                id, name, description, property_type, address, 
                size_acres, asking_price, listing_url, zoning, 
                thumbnail_url, status
            FROM "Georgia Properties" 
            WHERE id IN ({id_list})
            ORDER BY asking_price DESC
        """)
        
        with engine.connect() as connection:
            detailed_results = connection.execute(detailed_query).fetchall()
            
            properties = []
            for row in detailed_results:
                try:
                    # Parse address JSON
                    address_data = {}
                    if row[4]:  # address column
                        if isinstance(row[4], str):
                            import json
                            address_data = json.loads(row[4])
                        elif isinstance(row[4], dict):
                            address_data = row[4]
                    
                    # Create full address string
                    full_address = "Address not available"
                    if address_data:
                        address_parts = []
                        if address_data.get('street'):
                            address_parts.append(address_data['street'])
                        if address_data.get('city'):
                            address_parts.append(address_data['city'])
                        if address_data.get('state'):
                            address_parts.append(address_data['state'])
                        if address_data.get('zip'):
                            address_parts.append(str(address_data['zip']))
                        
                        if address_parts:
                            full_address = ', '.join(address_parts)
                            
                        # Update address_data with full address
                        address_data['fullAddress'] = full_address
                    
                    property_data = {
                        "id": row[0],
                        "name": row[1] or "Unnamed Property",
                        "description": row[2],
                        "property_type": row[3] or "Unknown",
                        "address": address_data,
                        "size_acres": float(row[5]) if row[5] else None,
                        "asking_price": float(row[6]) if row[6] else 0,
                        "listing_url": row[7],
                        "zoning": row[8],
                        "thumbnail_url": row[9],
                        "status": row[10] or "Available"
                    }
                    
                    properties.append(property_data)
                    
                except Exception as e:
                    print(f"Error processing property row: {e}")
                    continue
            
            return properties
            
    except Exception as e:
        print(f"Error fetching complete property details: {e}")
        # Fallback to basic parsing if detailed fetch fails
        return parse_query_results(results)

def parse_query_results(results):
    """Parse SQL query results into structured property objects"""
    properties = []
    
    for row in results:
        try:
            property_data = {
                "id": row[0] if len(row) > 0 and row[0] else 0,
                "name": row[1] if len(row) > 1 and row[1] else "Unnamed Property",
                "asking_price": 0,
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
                        property_data["asking_price"] = float(value)
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
    uvicorn.run(app, host="0.0.0.0", port=8003)