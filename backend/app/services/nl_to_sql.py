import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.database import get_db
from app.models.property import Property, QueryHistory
from app.models.schemas import PropertyResponse, PropertyAddress, ChatMessage
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json
import uuid
import time
import re

openai.api_key = settings.OPENAI_API_KEY

class NLToSQLService:
    def __init__(self):
        self.schema_info = self._get_schema_info()
        self.correction_history = []

    def _get_schema_info(self) -> str:
        return """
        Table: properties
        Columns:
        - id (UUID): Unique identifier
        - name (String): Property name/title
        - description (Text): Property description
        - property_type (String): Commercial, Industrial, Retail, Office, etc.
        - property_subtype (String): Warehouse, Shopping Center, etc.
        - address_street, address_city, address_state, address_zip, address_county (String): Address components
        - latitude, longitude (Float): Geographic coordinates
        - asking_price (Float): Listed price in USD
        - price_per_sqft (Float): Price per square foot
        - size_sqft (Float): Building square footage
        - size_acres (Float): Land size in acres
        - lot_size_sqft (Float): Lot size in square feet
        - year_built (Integer): Year of construction
        - zoning (String): Zoning classification
        - listing_date (DateTime): When property was listed
        - listing_url (String): External listing URL
        - thumbnail_url (String): Property image URL
        - is_active (Boolean): Whether listing is active
        """

    async def process_query(self, user_query: str, db: Session) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Generate SQL query
            sql_query = await self._generate_sql(user_query)
            
            # Execute query
            properties = self._execute_query(sql_query, db)
            
            # Convert to response format
            property_responses = self._convert_to_responses(properties)
            
            # Generate natural language response
            response_text = await self._generate_response(user_query, property_responses)
            
            # Save successful query to history
            self._save_query_history(db, user_query, sql_query, True, len(properties))
            
            execution_time = time.time() - start_time
            
            return {
                "message": ChatMessage(
                    id=str(uuid.uuid4()),
                    content=response_text,
                    type="assistant",
                    timestamp=datetime.utcnow(),
                    properties=property_responses
                ),
                "sql_query": sql_query,
                "execution_time": execution_time
            }
            
        except Exception as e:
            error_message = f"I encountered an error processing your request: {str(e)}"
            
            # Try to auto-correct if it's a SQL error
            if "sql" in str(e).lower() or "syntax" in str(e).lower():
                try:
                    corrected_sql = await self._correct_sql_error(user_query, str(e))
                    properties = self._execute_query(corrected_sql, db)
                    property_responses = self._convert_to_responses(properties)
                    response_text = await self._generate_response(user_query, property_responses)
                    
                    # Save corrected query
                    self._save_query_history(db, user_query, corrected_sql, True, len(properties))
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "message": ChatMessage(
                            id=str(uuid.uuid4()),
                            content=response_text + "\n\n(Note: I corrected a query error automatically)",
                            type="assistant",
                            timestamp=datetime.utcnow(),
                            properties=property_responses
                        ),
                        "sql_query": corrected_sql,
                        "execution_time": execution_time
                    }
                except:
                    pass  # Fall through to error response
            
            # Save failed query to history
            self._save_query_history(db, user_query, "", False, 0, str(e))
            
            return {
                "message": ChatMessage(
                    id=str(uuid.uuid4()),
                    content=error_message,
                    type="error",
                    timestamp=datetime.utcnow()
                ),
                "sql_query": None,
                "execution_time": time.time() - start_time
            }

    async def _generate_sql(self, user_query: str) -> str:
        system_prompt = f"""
        You are an expert SQL generator for a commercial real estate database.
        
        Database Schema:
        {self.schema_info}
        
        Important rules:
        1. Always use proper PostgreSQL syntax
        2. Use ILIKE for case-insensitive string matching
        3. Always include is_active = true in WHERE clause
        4. Use appropriate JOINs if needed
        5. Limit results to 50 unless specifically asked for more
        6. Use proper data types (Float for numbers, String for text)
        7. For price ranges, handle both asking_price and price_per_sqft
        8. For location queries, search in address_city, address_county, address_street
        
        Generate ONLY the SQL query, no explanations or additional text.
        """
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the SQL query
        sql_query = re.sub(r'^```sql\n?', '', sql_query)
        sql_query = re.sub(r'\n?```$', '', sql_query)
        sql_query = sql_query.strip()
        
        return sql_query

    async def _correct_sql_error(self, user_query: str, error: str) -> str:
        system_prompt = f"""
        You are an expert SQL error corrector for a commercial real estate database.
        
        Database Schema:
        {self.schema_info}
        
        The user asked: "{user_query}"
        
        The SQL query failed with this error: "{error}"
        
        Please provide a corrected SQL query that will work. Common issues:
        1. Column names not matching schema
        2. Incorrect syntax
        3. Missing table aliases
        4. Wrong data types
        
        Generate ONLY the corrected SQL query, no explanations.
        """
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()

    def _execute_query(self, sql_query: str, db: Session) -> List[Property]:
        try:
            result = db.execute(text(sql_query))
            return result.fetchall()
        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")

    def _convert_to_responses(self, properties: List) -> List[PropertyResponse]:
        responses = []
        for prop in properties:
            # Convert SQLAlchemy row to dict if needed
            if hasattr(prop, '_mapping'):
                prop_dict = dict(prop._mapping)
            else:
                prop_dict = prop._asdict() if hasattr(prop, '_asdict') else dict(prop)
                
            address = PropertyAddress(
                street=prop_dict.get('address_street'),
                city=prop_dict.get('address_city', ''),
                state=prop_dict.get('address_state', 'Georgia'),
                zip_code=prop_dict.get('address_zip'),
                county=prop_dict.get('address_county'),
                latitude=prop_dict.get('latitude'),
                longitude=prop_dict.get('longitude')
            )
            
            responses.append(PropertyResponse(
                id=prop_dict['id'],
                name=prop_dict['name'],
                description=prop_dict.get('description'),
                property_type=prop_dict['property_type'],
                property_subtype=prop_dict.get('property_subtype'),
                address=address,
                asking_price=prop_dict.get('asking_price'),
                price_per_sqft=prop_dict.get('price_per_sqft'),
                size_sqft=prop_dict.get('size_sqft'),
                size_acres=prop_dict.get('size_acres'),
                lot_size_sqft=prop_dict.get('lot_size_sqft'),
                year_built=prop_dict.get('year_built'),
                zoning=prop_dict.get('zoning'),
                listing_date=prop_dict['listing_date'],
                listing_url=prop_dict.get('listing_url'),
                thumbnail_url=prop_dict.get('thumbnail_url'),
                is_active=prop_dict.get('is_active', True),
                created_at=prop_dict['created_at'],
                updated_at=prop_dict['updated_at']
            ))
        return responses

    async def _generate_response(self, user_query: str, properties: List[PropertyResponse]) -> str:
        if not properties:
            return "I couldn't find any properties matching your criteria. Try adjusting your search terms or expanding your requirements."
        
        # Create a summary of the properties for the AI to use
        property_summary = []
        for prop in properties[:5]:  # Limit to first 5 for summary
            summary = f"- {prop.name}: {prop.property_type}"
            if prop.asking_price:
                summary += f", ${prop.asking_price:,.0f}"
            if prop.address.city:
                summary += f" in {prop.address.city}"
            property_summary.append(summary)
        
        system_prompt = """
        You are a helpful commercial real estate assistant. 
        Provide a natural, conversational response about the properties found.
        Be concise but informative. Include key details like count, types, and locations.
        """
        
        user_prompt = f"""
        User asked: "{user_query}"
        
        Found {len(properties)} properties:
        {chr(10).join(property_summary)}
        
        Provide a natural response about these findings.
        """
        
        response = await openai.ChatCompletion.acreate(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()

    def _save_query_history(self, db: Session, user_query: str, sql_query: str, 
                          success: bool, result_count: int, error_message: Optional[str] = None):
        try:
            history = QueryHistory(
                user_query=user_query,
                generated_sql=sql_query,
                execution_success=success,
                result_count=result_count,
                error_message=error_message
            )
            db.add(history)
            db.commit()
        except Exception as e:
            # Don't fail the main request if history saving fails
            print(f"Failed to save query history: {e}")

    def submit_feedback(self, db: Session, query_id: str, score: int):
        """Allow users to rate the quality of responses for learning purposes"""
        try:
            history = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
            if history:
                history.feedback_score = score
                db.commit()
        except Exception as e:
            print(f"Failed to save feedback: {e}")

# Global instance
nl_to_sql_service = NLToSQLService()