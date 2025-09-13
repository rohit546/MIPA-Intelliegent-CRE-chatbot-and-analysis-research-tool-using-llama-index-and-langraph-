"""
Enhanced App with Self-Correcting SQL Feedback Loop
Integrates the feedback loop with the existing Georgia Properties pipeline
"""

import os
import sys
import json
from config import OPENAI_API_KEY, DATABASE_URL
from sqlalchemy import create_engine, text
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.query_engine import NLSQLTableQueryEngine
from query_parser import QueryParser, SQLGenerator
from enhanced_sql_integration import EnhancedSQLGenerator, FeedbackLoopReporter

def setup_enhanced_query_engine(database_url: str, openai_api_key: str):
    """Setup the enhanced query engine with feedback loop"""
    
    # Initialize the enhanced SQL generator
    enhanced_generator = EnhancedSQLGenerator(database_url, openai_api_key)
    
    # Create database connection
    engine = create_engine(database_url)
    
    # Setup LlamaIndex
    Settings.llm = OpenAI(api_key=openai_api_key, model="gpt-4", temperature=0)
    Settings.embed_model = OpenAIEmbedding(api_key=openai_api_key)
    
    # Create SQL database wrapper
    sql_database = SQLDatabase(
        engine, 
        include_tables=["Georgia Properties"],
        sample_rows_in_table_info=3
    )
    
    # Enhanced system prompt with feedback loop awareness
    system_prompt = """You are a PostgreSQL expert generating queries for Georgia commercial properties.
The system includes a self-correcting feedback loop that will validate and improve your queries.

MANDATORY RULES:
1. ALWAYS use LIMIT 50 unless user specifies otherwise
2. ALWAYS use ORDER BY (asking_price ASC for budget queries, asking_price DESC for general)
3. ALWAYS use ILIKE with wildcards for text matching
4. ALWAYS check BOTH property_type AND property_subtype columns
5. ALWAYS include asking_price in SELECT clause for context
6. ALWAYS include asking_price IS NOT NULL when price matters

COUNTY SEARCH PATTERNS (CRITICAL - FEEDBACK LOOP WILL CORRECT THESE):
- For counties: NEVER search property_type/property_subtype for county names!
- ALWAYS use address->>'county' ILIKE '%county_name%' for county searches
- Alternative: address::text ILIKE '%county_name%'
- Georgia counties: Dekalb, Fulton, Gwinnett, Walton, Cobb, Clayton, Henry, etc.

AGGREGATION QUERIES (FEEDBACK LOOP AWARE):
- For COUNT queries: Use COUNT(*) or COUNT(column_name)
- GROUP BY appropriately (avoid asking_price in GROUP BY for count queries)
- For statistics: Use proper aggregation functions (AVG, SUM, MAX, MIN)

SIZE SEARCH PATTERNS:
- Square footage: Use size_sqft for lot size OR building_sqft for building size
- Acres: Use size_acres for land area
- Always include IS NOT NULL AND > 0 for size filters
- Use BETWEEN for ranges: size_acres BETWEEN 2 AND 5

FEEDBACK LOOP INTEGRATION:
- Your queries will be automatically validated and corrected if needed
- Common corrections: county filters, aggregation syntax, result count optimization
- Learning system improves suggestions over time

COLUMN PRIORITY (ALWAYS INCLUDE THESE):
Core: id, name, property_type, property_subtype, asking_price
Links: listing_url (contains Crexi links)
Size: size_acres, size_sqft, building_sqft  
Location: address (as JSONB), zoning
Enrichment: traffic_count_aadt, population_1mi, projected_roi_percent, median_income

REQUIRED SELECT PATTERN (always include these columns):
SELECT id, name, property_type, property_subtype, asking_price, 
       listing_url, address, zoning,
       COALESCE(size_acres, 0) as acres,
       COALESCE(size_sqft, 0) as lot_sqft,
       COALESCE(building_sqft, 0) as building_sqft
FROM "Georgia Properties"
WHERE [conditions]
ORDER BY asking_price ASC
LIMIT 50;

EXAMPLES (will be auto-corrected if wrong):
User: "how many counties have properties"
SQL: SELECT address->>'county' as county, COUNT(*) as property_count
FROM "Georgia Properties"
WHERE address->>'county' IS NOT NULL
GROUP BY address->>'county'
ORDER BY property_count DESC;

User: "properties of 2 and 5 acres in walton county"
SQL: SELECT id, name, property_type, property_subtype, asking_price, 
       listing_url, address, zoning, size_acres
FROM "Georgia Properties"
WHERE address->>'county' ILIKE '%walton%'
AND size_acres IS NOT NULL AND size_acres > 0
AND (size_acres = 2 OR size_acres = 5)
ORDER BY size_acres ASC LIMIT 50;

User: "gas stations under $500k"
SQL: SELECT id, name, property_type, property_subtype, asking_price,
       listing_url, address, zoning, size_acres, building_sqft
FROM "Georgia Properties"
WHERE (property_type ILIKE '%gas%' OR property_subtype ILIKE '%gas%' OR property_type ILIKE '%station%')
AND asking_price IS NOT NULL AND asking_price < 500000
ORDER BY asking_price ASC LIMIT 50;
"""
    
    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["Georgia Properties"],
        return_raw=True,
        verbose=True,
        synthesize_response=False,
        system_prompt=system_prompt
    )
    
    return query_engine, enhanced_generator, engine

def enhanced_query_with_feedback(user_query: str, query_engine, enhanced_generator, engine):
    """Process query with feedback loop integration"""
    
    print(f"\n🔄 Processing query through enhanced pipeline...")
    
    try:
        # Step 1: Generate initial query with GPT-4
        print("📝 Step 1: Generating initial SQL with GPT-4...")
        response = query_engine.query(user_query)
        
        # Extract generated SQL
        gpt4_sql = None
        if hasattr(response, 'metadata') and 'sql_query' in response.metadata:
            gpt4_sql = response.metadata['sql_query']
            print(f"   Generated SQL: {gpt4_sql[:100]}...")
        
        if not gpt4_sql:
            print("   ❌ No SQL generated by GPT-4")
            return response
        
        # Step 2: Process through feedback loop
        print("🔍 Step 2: Validating and correcting SQL...")
        enhanced_result = enhanced_generator.generate_and_validate_sql(user_query, gpt4_sql)
        
        # Step 3: Report feedback loop results
        print("📊 Step 3: Feedback loop results:")
        print(f"   Status: {enhanced_result['validation_status']}")
        print(f"   Iterations: {enhanced_result['iteration_count']}")
        
        if enhanced_result['was_corrected']:
            print(f"   🔧 Corrections applied: {enhanced_result['explanation']}")
            print(f"   Final SQL: {enhanced_result['final_sql'][:100]}...")
        else:
            print("   ✅ Original SQL was valid")
        
        # Step 4: Update response with enhanced results
        if hasattr(response, 'metadata'):
            response.metadata.update({
                'enhanced_sql': enhanced_result['final_sql'],
                'validation_status': enhanced_result['validation_status'],
                'was_corrected': enhanced_result['was_corrected'],
                'correction_explanation': enhanced_result['explanation'],
                'sql_query': enhanced_result['final_sql']  # Use corrected SQL
            })
            
            # Use enhanced results
            if enhanced_result['results'].rows:
                response.metadata['result'] = enhanced_result['results'].rows
        
        return response
    
    except Exception as e:
        print(f"❌ Enhanced processing error: {e}")
        # Fallback to original query engine
        return query_engine.query(user_query)

def display_enhanced_results(response, enhanced_result=None):
    """Display results with feedback loop information"""
    
    print(f"\n✅ Enhanced Results:")
    print("-" * 70)
    
    # Show feedback loop status
    if hasattr(response, 'metadata'):
        metadata = response.metadata
        
        if 'validation_status' in metadata:
            status = metadata['validation_status']
            print(f"🔍 Validation Status: {status}")
            
            if metadata.get('was_corrected', False):
                print(f"🔧 Query Corrections: {metadata.get('correction_explanation', 'N/A')}")
        
        # Show SQL query
        sql_query = metadata.get('enhanced_sql') or metadata.get('sql_query', '')
        if sql_query:
            print(f"📊 Final SQL: {sql_query}")
        
        # Show results
        if 'result' in metadata:
            results = metadata['result']
            print(f"\n📈 Found {len(results)} properties:")
            print("=" * 70)
            
            for i, row in enumerate(results[:20], 1):  # Show first 20
                try:
                    # Create property data dictionary for easier access
                    property_data = {}
                    
                    # Map common column positions (adjust based on SQL SELECT order)
                    if len(row) >= 1:
                        property_data['id'] = row[0] if row[0] is not None else "N/A"
                    if len(row) >= 2:
                        property_data['name'] = row[1] if row[1] is not None else "Unnamed Property"
                    
                    # Parse other columns dynamically
                    for col_idx in range(2, len(row)):
                        col_value = row[col_idx]
                        if col_value is None:
                            continue
                        
                        # Identify column types based on content
                        if isinstance(col_value, str):
                            if col_value.startswith('https://www.crexi.com'):
                                property_data['crexi_url'] = col_value
                            elif '{' in col_value and ('street' in col_value.lower() or 'city' in col_value.lower()):
                                property_data['address'] = col_value
                            elif any(word in col_value.lower() for word in ['land', 'retail', 'commercial', 'gas', 'restaurant']):
                                if 'property_type' not in property_data:
                                    property_data['property_type'] = col_value
                                else:
                                    property_data['property_subtype'] = col_value
                            elif any(word in col_value.lower() for word in ['residential', 'commercial', 'industrial', 'agricultural']):
                                property_data['zoning'] = col_value
                        elif isinstance(col_value, (int, float)):
                            if col_value >= 10000:  # Likely a price
                                property_data['price'] = col_value
                            elif 0.01 <= col_value <= 1000:  # Likely acres
                                property_data['size_acres'] = col_value
                            elif col_value > 1000:  # Likely sqft
                                property_data['size_sqft'] = col_value
                    
                    # Display formatted property information
                    print(f"\n🏢 Property #{i}")
                    print(f"   ID: {property_data.get('id', 'N/A')}")
                    print(f"   📛 Name: {property_data.get('name', 'Unnamed Property')}")
                    
                    # Price information
                    if 'price' in property_data:
                        price = property_data['price']
                        if price >= 1000000:
                            print(f"   💰 Price: ${price/1000000:.2f}M")
                        elif price >= 1000:
                            print(f"   💰 Price: ${price/1000:.0f}K")
                        else:
                            print(f"   💰 Price: ${price:,.2f}")
                    
                    # Size information
                    size_info = []
                    if 'size_acres' in property_data:
                        acres = property_data['size_acres']
                        size_info.append(f"{acres} acres")
                    if 'size_sqft' in property_data:
                        sqft = property_data['size_sqft']
                        size_info.append(f"{sqft:,.0f} sqft")
                    if size_info:
                        print(f"   📏 Size: {' • '.join(size_info)}")
                    
                    # Property type and zoning
                    if 'property_type' in property_data:
                        print(f"   🏪 Type: {property_data['property_type']}")
                    if 'property_subtype' in property_data:
                        print(f"   🏷️  Subtype: {property_data['property_subtype']}")
                    if 'zoning' in property_data:
                        print(f"   🗺️  Zoning: {property_data['zoning']}")
                    
                    # Address information
                    if 'address' in property_data:
                        try:
                            import json
                            addr = json.loads(property_data['address'].replace("'", '"'))
                            street = addr.get('street', 'N/A')
                            city = addr.get('city', 'N/A')
                            county = addr.get('county', 'N/A')
                            zip_code = addr.get('zip', 'N/A')
                            print(f"   📍 Address: {street}")
                            print(f"      📍 Location: {city}, {county} {zip_code}")
                        except:
                            # Fallback for non-JSON address format
                            print(f"   📍 Address: {property_data['address']}")
                    
                    # Crexi link
                    if 'crexi_url' in property_data:
                        print(f"   🔗 Crexi Link: {property_data['crexi_url']}")
                    
                    print("-" * 70)
                    
                except Exception as e:
                    # Fallback to simple display
                    print(f"\n🏢 Property #{i}")
                    print(f"   Raw data: {row}")
                    print(f"   Display error: {e}")
                    print("-" * 70)

def main():
    try:
        print("🚀 Initializing Enhanced Georgia Properties Search with Feedback Loop...")
        
        # Setup enhanced query engine
        query_engine, enhanced_generator, engine = setup_enhanced_query_engine(DATABASE_URL, OPENAI_API_KEY)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM "Georgia Properties"'))
            count = result.scalar()
            print(f"✅ Connected! Found {count} properties in database.")
        
        # Initialize feedback loop reporter
        reporter = FeedbackLoopReporter(enhanced_generator)
        
        print("\n" + "="*60)
        print("🏢 GEORGIA PROPERTIES - ENHANCED NL-TO-SQL WITH LEARNING")
        print("="*60)
        print("✨ NEW FEATURES:")
        print("• Self-correcting SQL queries")
        print("• Learning from mistakes")
        print("• Intelligent validation")
        print("• Performance optimization")
        
        print("\n📍 EXAMPLE QUERIES:")
        print("- 'How many counties have retail properties?'")
        print("- 'Gas stations in Walton County under $500k'")
        print("- 'Properties between 2-5 acres with traffic data'")
        print("- 'Count of every county with properties'")
        
        print("\n💡 FEEDBACK LOOP COMMANDS:")
        print("- Type 'stats' to see learning statistics")
        print("- Type 'report' to see performance report")
        print("- Type 'insights' to see recommendations")
        print("\nType 'exit' to quit.")
        print("="*60)
        
        while True:
            try:
                query = input("\n🔍 Your question: ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("\n📊 Final Performance Report:")
                    print(reporter.generate_performance_report())
                    print("Goodbye! 👋")
                    break
                
                # Special commands
                if query.lower() == 'stats':
                    stats = enhanced_generator.get_learning_insights()
                    print(f"\n📊 Learning Statistics:")
                    print(json.dumps(stats, indent=2))
                    continue
                
                if query.lower() == 'report':
                    print(reporter.generate_performance_report())
                    continue
                
                if query.lower() == 'insights':
                    recommendations = reporter.get_correction_recommendations()
                    print(f"\n💡 Recommendations:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"{i}. {rec}")
                    continue
                
                if not query:
                    continue
                
                print(f"\n⏳ Processing enhanced query...")
                
                # Process query through enhanced pipeline
                response = enhanced_query_with_feedback(
                    query, query_engine, enhanced_generator, engine
                )
                
                # Display enhanced results
                display_enhanced_results(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try rephrasing your question.")
                
    except Exception as e:
        print(f"❌ Setup Error: {str(e)}")
        print("Please check your database connection and API key.")
        sys.exit(1)

if __name__ == "__main__":
    main()