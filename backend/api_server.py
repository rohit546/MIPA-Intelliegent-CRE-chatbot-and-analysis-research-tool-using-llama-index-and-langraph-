"""
FastAPI Server for connecting frontend chatbot to LlamaIndex backend
Preserves all existing functionality in app_enhanced.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import sys
import os
from typing import List, Dict, Any, Optional
import uvicorn

# Import the existing enhanced functionality
from app_enhanced import setup_enhanced_query_engine, enhanced_query_with_feedback
from config import OPENAI_API_KEY, DATABASE_URL

app = FastAPI(title="Georgia Properties Chatbot API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for query engine (initialized on startup)
query_engine = None
enhanced_generator = None
db_engine = None

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    properties: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None
    validation_status: Optional[str] = None
    was_corrected: Optional[bool] = None
    correction_explanation: Optional[str] = None

def extract_properties_from_response(response) -> List[Dict[str, Any]]:
    """Extract property data from LlamaIndex response and format for frontend"""
    properties = []
    
    if not hasattr(response, 'metadata') or 'result' not in response.metadata:
        return properties
    
    results = response.metadata['result']
    
    for row in results:
        try:
            property_data = {
                'id': None,
                'name': None,
                'property_type': None,
                'asking_price': None,
                'address': None,
                'thumbnail_url': None,
                'listing_url': None,
                'size_acres': None,
                'size_sqft': None,
                'building_sqft': None,
                'zoning': None,
                'property_subtype': None,
                'description': None
            }
            
            # Map database columns to frontend format - handle dynamic column mapping
            if len(row) >= 1 and row[0] is not None:
                property_data['id'] = row[0]
            if len(row) >= 2 and row[1] is not None:
                property_data['name'] = row[1]
                
            # Parse remaining columns more intelligently
            for col_idx in range(len(row)):
                col_value = row[col_idx]
                if col_value is None:
                    continue
                
                if isinstance(col_value, str):
                    # Thumbnail URL detection
                    if col_value.startswith('http') and any(ext in col_value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        property_data['thumbnail_url'] = col_value
                    # Crexi listing URL
                    elif col_value.startswith('https://www.crexi.com'):
                        property_data['listing_url'] = col_value
                    # Address parsing
                    elif '{' in col_value and ('street' in col_value.lower() or 'city' in col_value.lower()):
                        try:
                            addr_dict = json.loads(col_value.replace("'", '"'))
                            street = addr_dict.get('street', '')
                            city = addr_dict.get('city', '')
                            state = addr_dict.get('state', 'GA')
                            zip_code = addr_dict.get('zip', '')
                            county = addr_dict.get('county', '')
                            
                            property_data['address'] = {
                                'fullAddress': f"{street}, {city}, {state} {zip_code}".strip(', '),
                                'street': street,
                                'city': city,
                                'state': state,
                                'zip': zip_code,
                                'county': county
                            }
                        except:
                            property_data['address'] = {'fullAddress': str(col_value)}
                    # Property type detection
                    elif any(word in col_value.lower() for word in ['gas', 'station', 'convenience', 'retail', 'commercial', 'restaurant', 'office', 'industrial', 'land', 'warehouse']):
                        if property_data['property_type'] is None:
                            property_data['property_type'] = col_value
                        else:
                            property_data['property_subtype'] = col_value
                    # Zoning
                    elif any(word in col_value.lower() for word in ['residential', 'commercial', 'industrial', 'agricultural', 'mixed']):
                        property_data['zoning'] = col_value
                    # Description
                    elif len(col_value) > 50 and col_idx > 5:  # Longer text, likely description
                        property_data['description'] = col_value[:200] + '...' if len(col_value) > 200 else col_value
                        
                elif isinstance(col_value, (int, float)):
                    if col_value >= 10000:  # Likely a price
                        property_data['asking_price'] = col_value
                    elif 0.01 <= col_value <= 1000:  # Likely acres
                        property_data['size_acres'] = col_value
                    elif col_value > 1000 and col_value < 10000000:  # Likely sqft
                        if property_data['size_sqft'] is None:
                            property_data['size_sqft'] = col_value
                        elif property_data['building_sqft'] is None:
                            property_data['building_sqft'] = col_value
            
            # Generate placeholder thumbnail if none exists
            if not property_data['thumbnail_url']:
                # Use a property type based placeholder
                property_type = (property_data['property_type'] or '').lower()
                if 'gas' in property_type or 'station' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=400&h=300&fit=crop'
                elif 'retail' in property_type or 'commercial' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1556636530-9e82eded7d4d?w=400&h=300&fit=crop'  
                elif 'office' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1582653291997-079a1c04e5a1?w=400&h=300&fit=crop'
                elif 'industrial' in property_type or 'warehouse' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop'
                else:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop'
            
            properties.append(property_data)
            
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue
    
    return properties

@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced query engine on server startup"""
    global query_engine, enhanced_generator, db_engine
    
    try:
        print("🚀 Initializing Enhanced Georgia Properties Query Engine...")
        query_engine, enhanced_generator, db_engine = setup_enhanced_query_engine(DATABASE_URL, OPENAI_API_KEY)
        
        # Test connection
        from sqlalchemy import text
        with db_engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM "Georgia Properties"'))
            count = result.scalar()
            print(f"✅ Connected! Found {count} properties in database.")
        
    except Exception as e:
        print(f"❌ Failed to initialize query engine: {e}")
        raise e

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Georgia Properties Chatbot API is running!", "status": "healthy"}

@app.post("/api/chat/send", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """Process natural language queries and return property results"""
    
    if not query_engine or not enhanced_generator:
        raise HTTPException(status_code=503, detail="Query engine not initialized")
    
    try:
        user_query = chat_message.message.strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        print(f"🔍 Processing query: {user_query}")
        
        # Process through enhanced pipeline
        response = enhanced_query_with_feedback(
            user_query, query_engine, enhanced_generator, db_engine
        )
        
        # Extract properties for frontend display
        properties = extract_properties_from_response(response)
        
        # Build response message
        if properties:
            property_count = len(properties)
            response_text = f"Found {property_count} properties matching your query!"
            
            # Add a summary of the first few properties
            if property_count <= 3:
                response_text += "\n\n"
                for i, prop in enumerate(properties[:3], 1):
                    name = prop.get('name') or 'Property'
                    price = prop.get('asking_price')
                    if price:
                        price_str = f"${price:,.0f}" if price < 1000000 else f"${price/1000000:.1f}M"
                        response_text += f"{i}. {name} - {price_str}\n"
                    else:
                        response_text += f"{i}. {name}\n"
            else:
                response_text += f" Check the property results panel to see all {property_count} matching properties with images and details."
        else:
            # Get better error messaging based on the query
            query_lower = user_query.lower()
            if 'gas station' in query_lower or 'gas' in query_lower:
                response_text = "I couldn't find properties with the exact term 'Gas Station'. Let me search for related terms like 'convenience store', 'fuel', or 'petroleum' properties. The database might use different terminology."
            else:
                response_text = "I couldn't find any properties matching your exact query. Try rephrasing your request or being more general. For example: 'retail properties under $1M' or 'commercial properties in Atlanta'."
        
        # Extract metadata
        metadata = response.metadata if hasattr(response, 'metadata') else {}
        
        return ChatResponse(
            response=response_text,
            properties=properties,
            sql_query=metadata.get('enhanced_sql') or metadata.get('sql_query'),
            validation_status=metadata.get('validation_status'),
            was_corrected=metadata.get('was_corrected', False),
            correction_explanation=metadata.get('correction_explanation')
        )
        
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing your query: {str(e)}"
        )

@app.get("/api/chat/address")
async def fetch_address_details(address: str):
    """Fetch details for a specific address (placeholder for future enhancement)"""
    
    # This could be enhanced to query specific address information
    # For now, return a basic response
    return {
        "address": address,
        "details": "Address details functionality to be implemented",
        "status": "placeholder"
    }

@app.get("/api/property-types")
async def get_property_types():
    """Get all unique property types and subtypes for better query matching"""
    
    if not db_engine:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        from sqlalchemy import text
        
        # Get unique property types and subtypes
        query = '''
        SELECT 
            property_type, 
            property_subtype,
            COUNT(*) as count
        FROM "Georgia Properties" 
        WHERE property_type IS NOT NULL 
           OR property_subtype IS NOT NULL
        GROUP BY property_type, property_subtype
        ORDER BY count DESC
        LIMIT 100
        '''
        
        with db_engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
        
        types_data = []
        for row in rows:
            types_data.append({
                'property_type': row[0],
                'property_subtype': row[1], 
                'count': row[2]
            })
        
        return {"property_types": types_data}
        
    except Exception as e:
        print(f"❌ Property types query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties")
async def get_properties(
    page: int = 1,
    limit: int = 20,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get properties with filtering and pagination (compatible with existing frontend)"""
    
    if not db_engine:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        from sqlalchemy import text
        
        # Build SQL query with filters
        conditions = []
        params = {}
        
        if property_type:
            conditions.append("(property_type ILIKE :property_type OR property_subtype ILIKE :property_type)")
            params['property_type'] = f"%{property_type}%"
        
        if min_price:
            conditions.append("asking_price >= :min_price")
            params['min_price'] = min_price
        
        if max_price:
            conditions.append("asking_price <= :max_price")
            params['max_price'] = max_price
        
        # Add non-null constraints
        conditions.append("asking_price IS NOT NULL")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else "WHERE asking_price IS NOT NULL"
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build final query
        sql_query = f'''
        SELECT id, name, property_type, property_subtype, asking_price, 
               listing_url, address, zoning,
               COALESCE(size_acres, 0) as size_acres,
               COALESCE(size_sqft, 0) as size_sqft,
               COALESCE(building_sqft, 0) as building_sqft
        FROM "Georgia Properties"
        {where_clause}
        ORDER BY asking_price ASC
        LIMIT :limit OFFSET :offset
        '''
        
        params.update({'limit': limit, 'offset': offset})
        
        with db_engine.connect() as conn:
            result = conn.execute(text(sql_query), params)
            rows = result.fetchall()
        
        # Format properties for frontend
        properties = []
        for row in rows:
            try:
                # Parse address JSON if present
                address_data = None
                if row[6]:  # address column
                    try:
                        addr_str = str(row[6]).replace("'", '"')
                        addr_dict = json.loads(addr_str)
                        address_data = {
                            'fullAddress': f"{addr_dict.get('street', '')}, {addr_dict.get('city', '')}, {addr_dict.get('state', 'GA')} {addr_dict.get('zip', '')}".strip(', '),
                            'street': addr_dict.get('street'),
                            'city': addr_dict.get('city'),
                            'state': addr_dict.get('state', 'GA'),
                            'zip': addr_dict.get('zip'),
                            'county': addr_dict.get('county')
                        }
                    except:
                        address_data = {'fullAddress': str(row[6])}
                
                property_data = {
                    'id': row[0],
                    'name': row[1] or 'Unnamed Property',
                    'property_type': row[2] or row[3],  # Use property_type or property_subtype
                    'asking_price': float(row[4]) if row[4] else None,
                    'address': address_data,
                    'thumbnail_url': None,  # Will be set below
                    'listing_url': row[5],
                    'zoning': row[7],
                    'size_acres': float(row[8]) if row[8] else None,
                    'size_sqft': float(row[9]) if row[9] else None,
                    'building_sqft': float(row[10]) if row[10] else None
                }
                
                # Generate placeholder thumbnail based on property type
                property_type = (property_data['property_type'] or '').lower()
                if 'gas' in property_type or 'station' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=400&h=300&fit=crop'
                elif 'retail' in property_type or 'commercial' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1556636530-9e82eded7d4d?w=400&h=300&fit=crop'  
                elif 'office' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1582653291997-079a1c04e5a1?w=400&h=300&fit=crop'
                elif 'industrial' in property_type or 'warehouse' in property_type:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop'
                else:
                    property_data['thumbnail_url'] = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop'
                
                properties.append(property_data)
                
            except Exception as e:
                print(f"Error formatting property row: {e}")
                continue
        
        return {
            "properties": properties,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(properties)
            }
        }
        
    except Exception as e:
        print(f"❌ Properties query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting Georgia Properties Chatbot API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)