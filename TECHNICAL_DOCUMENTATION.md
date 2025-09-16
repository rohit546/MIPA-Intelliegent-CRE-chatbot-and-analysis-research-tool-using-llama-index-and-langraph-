# MIPA - Technical Documentation
## Complete Request Flow and Feature Implementation Guide

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Frontend to Backend Request Flow](#frontend-to-backend-request-flow)
3. [Property Fetching Flow](#property-fetching-flow)
4. [AI Chat Query Processing](#ai-chat-query-processing)
5. [Self-Feedback Loop System](#self-feedback-loop-system)
6. [Address Analysis Flow](#address-analysis-flow)
7. [Database Schema and Queries](#database-schema-and-queries)
8. [Error Handling and Validation](#error-handling-and-validation)
9. [API Endpoints Reference](#api-endpoints-reference)
10. [Code File Dependencies](#code-file-dependencies)

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  React App (Port 3000)                                         │
│  ├── App.jsx (Router)                                          │
│  ├── ChatPage.jsx (Main Interface)                             │
│  ├── Chatbot.jsx (Chat Component)                              │
│  ├── QueryMode.jsx (AI Query Handler)                          │
│  ├── PropertyCard.tsx (Property Display)                       │
│  └── Services Layer                                             │
│      ├── api.js (Property API)                                 │
│      └── chatService.js (Chat API)                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP Requests
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server (Port 8003)                                    │
│  ├── api.py (Main Server)                                      │
│  ├── enhanced_sql_integration.py (AI Integration)              │
│  ├── query_parser.py (NLP Processing)                          │
│  ├── sql_feedback_loop.py (Self-Correction)                    │
│  └── smarty_address_analyzer_new.py (Address Enrichment)       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ SQL Queries
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                           │
│  ├── Georgia Properties Table                                  │
│  ├── Property Data (JSON)                                      │
│  └── Crexi Integration Links                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ External API Calls
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│  ├── OpenAI API (GPT-4)                                        │
│  ├── Smarty Streets API (Address Enrichment)                   │
│  └── Crexi (Property Listings)                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend to Backend Request Flow

### 1. Application Initialization

**File: `frontend/src/index.js`**
```javascript
// Entry point - loads React app
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

**File: `frontend/src/App.jsx`**
```javascript
// Main app component with routing
function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <div className="flex">
            <Sidebar />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/properties" element={<PropertiesPage />} />
                // ... other routes
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}
```

### 2. Chat Page Initialization

**File: `frontend/src/pages/ChatPage.jsx`**
```javascript
const ChatPage = () => {
  const [chatProperties, setChatProperties] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [showProperties, setShowProperties] = useState(false);

  // Handles property results from AI queries
  const handlePropertiesFound = (properties, query) => {
    setChatProperties(properties);
    setCurrentQuery(query);
    setShowProperties(true);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Chat Interface */}
      <Card className="h-[600px]">
        <Chatbot onPropertiesFound={handlePropertiesFound} />
      </Card>
      
      {/* Property Results */}
      <div className="h-[600px]">
        {showProperties && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {currentProperties.map((property, index) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

---

## Property Fetching Flow

### Scenario: User clicks "Properties" in sidebar

### Step 1: Frontend Navigation
**File: `frontend/src/components/Layout/Sidebar.jsx`**
```javascript
// User clicks "Properties" link
<Link to="/properties" className="sidebar-link">
  <Building className="h-5 w-5" />
  Properties
</Link>
```

### Step 2: Properties Page Load
**File: `frontend/src/pages/PropertiesPage.jsx`**
```javascript
const PropertiesPage = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    page: 1,
    limit: 20,
    property_type: null,
    min_price: null,
    max_price: null
  });

  // Fetch properties on component mount
  useEffect(() => {
    fetchProperties();
  }, [filters]);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      const response = await propertyService.fetchProperties(filters);
      setProperties(response.properties);
    } catch (error) {
      console.error('Error fetching properties:', error);
    } finally {
      setLoading(false);
    }
  };
};
```

### Step 3: API Service Call
**File: `frontend/src/services/api.js`**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';

export const fetchProperties = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // Add pagination
    params.append('page', filters.page || 1);
    params.append('limit', filters.limit || 20);
    
    // Add filters
    if (filters.property_type) {
      params.append('property_type', filters.property_type);
    }
    if (filters.min_price) {
      params.append('min_price', filters.min_price);
    }
    if (filters.max_price) {
      params.append('max_price', filters.max_price);
    }
    
    // HTTP GET request to backend
    const response = await api.get(`/properties?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
};
```

### Step 4: Backend API Endpoint
**File: `backend/api.py`**
```python
@app.get("/properties", response_model=PropertiesResponse)
async def get_properties(
    page: int = 1, 
    limit: int = 20,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None
):
    """Get properties for the gallery with pagination and filtering"""
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
            # Get total count for pagination
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
                    
                    properties.append({
                        "id": row[0],
                        "name": row[1] or "Unnamed Property",
                        "asking_price": float(row[4]) if row[4] else 0,
                        "size_acres": float(row[7]) if row[7] else None,
                        "property_type": row[2] or row[3] or "Unknown",
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
            total_pages = (total_count + limit - 1) // limit
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
```

### Step 5: Response Processing
**File: `frontend/src/pages/PropertiesPage.jsx`**
```javascript
// Response received from backend
const response = {
  properties: [
    {
      id: 1,
      name: "Commercial Property",
      asking_price: 500000,
      property_type: "retail",
      address: { fullAddress: "123 Main St, Atlanta, GA" },
      listing_url: "https://crexi.com/property/123",
      // ... other fields
    }
  ],
  pagination: {
    current_page: 1,
    total_pages: 5,
    total_count: 100,
    has_next: true,
    has_prev: false
  }
};

// Properties displayed in PropertyCard components
{properties.map(property => (
  <PropertyCard key={property.id} property={property} />
))}
```

---

## AI Chat Query Processing

### Scenario: User types "Show me gas stations under $500k" in chat

### Step 1: User Input in Chat Interface
**File: `frontend/src/components/Chatbot/QueryMode.jsx`**
```javascript
const QueryMode = ({ onPropertiesFound }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendQuery = async () => {
    if (!query.trim()) return;

    // Add user message to chat
    const userMessage = { type: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send query to backend
      const response = await sendMessage(query);
      
      // Add bot response to chat
      const botMessage = { 
        type: 'bot', 
        content: response.response,
        metadata: {
          sql_query: response.sql_query,
          validation_status: response.validation_status,
          was_corrected: response.was_corrected,
          correction_explanation: response.correction_explanation
        }
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // If properties found, display them
      if (response.properties && response.properties.length > 0) {
        onPropertiesFound(response.properties, query);
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = { 
        type: 'bot', 
        content: `❌ Error: ${error.message}` 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }

    setQuery('');
  };
};
```

### Step 2: Chat Service API Call
**File: `frontend/src/services/chatService.js`**
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';

export const sendMessage = async (message) => {
  try {
    // POST request to /chat endpoint
    const response = await axios.post(`${API_URL}/chat`, { message });
    return response.data;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};
```

### Step 3: Backend Chat Endpoint
**File: `backend/api.py`**
```python
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint - processes natural language queries"""
    try:
        user_query = request.message.strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # Check for simple greetings
        if user_query.lower() in ["hello", "hi", "hey", "help"]:
            return ChatResponse(
                response="Hi! I can help you find commercial properties in Georgia...",
                properties=[]
            )
        
        # Process query through enhanced SQL generation
        # Step 1: Parse the query to get structured filters
        parsed_query = enhanced_generator.query_parser.parse(user_query)
        
        # Step 2: Generate SQL query from parsed query
        gpt4_query = enhanced_generator.sql_generator.generate(parsed_query)
        
        # Step 3: Use enhanced generator to validate and execute
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
            response_text = "No properties found matching your criteria."
        
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
```

### Step 4: Query Parsing (NLP Processing)
**File: `backend/query_parser.py`**
```python
class QueryParser:
    def parse(self, query: str) -> ParsedQuery:
        """Main parsing entry point"""
        self.reset()
        query_lower = query.lower().strip()
        
        # Parse different components
        self._parse_location(query_lower)      # Counties, cities
        self._parse_property_type(query_lower) # Gas stations, retail, etc.
        self._parse_status(query_lower)        # Vacant, for sale, etc.
        self._parse_size(query_lower)          # Acres, square feet
        self._parse_price(query_lower)         # Price ranges
        self._parse_ordering(query_lower)      # Sort order
        self._determine_columns()              # Select columns
        
        return ParsedQuery(
            filters=self.filters,
            columns=self.columns,
            order_by=self.order_by,
            limit=self.limit
        )
    
    def _parse_property_type(self, query: str):
        """Parse property types with synonym expansion"""
        found_types = []
        
        for canonical_type, synonyms in self.PROPERTY_SYNONYMS.items():
            for synonym in synonyms:
                if re.search(rf'\b{re.escape(synonym)}\b', query):
                    found_types.extend(synonyms)
                    break
        
        if found_types:
            unique_types = list(set(found_types))
            self.filters.append(QueryFilter(
                FilterType.PROPERTY_TYPE,
                'ILIKE_OR',
                unique_types
            ))
    
    def _parse_price(self, query: str):
        """Parse price requirements with k/m notation support"""
        # Pattern for "under $X"
        under_match = re.search(self.PRICE_PATTERNS['under'], query)
        if under_match:
            max_price = normalize_price(under_match.group(1))
            self.filters.append(QueryFilter(FilterType.PRICE, '<=', max_price))
```

### Step 5: SQL Generation
**File: `backend/query_parser.py`**
```python
class SQLGenerator:
    def generate(self, parsed_query: ParsedQuery) -> str:
        """Generate SQL from parsed query"""
        
        # Build SELECT clause
        select_clause = f"SELECT {', '.join(parsed_query.columns)}"
        
        # Build FROM clause
        from_clause = f'FROM "{self.table_name}"'
        
        # Build WHERE clause
        where_conditions = []
        for filter_item in parsed_query.filters:
            condition = self._build_condition(filter_item)
            if condition:
                where_conditions.append(condition)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build ORDER BY clause
        order_clause = ""
        if parsed_query.order_by:
            column, direction = parsed_query.order_by
            order_clause = f"ORDER BY {column} {direction}"
        
        # Build LIMIT clause
        limit_clause = f"LIMIT {parsed_query.limit}"
        
        # Combine all clauses
        sql_parts = [select_clause, from_clause, where_clause, order_clause, limit_clause]
        sql = "\n".join(part for part in sql_parts if part)
        
        return sql
    
    def _build_condition(self, filter_item: QueryFilter) -> str:
        """Build individual WHERE condition"""
        if filter_item.filter_type == FilterType.PROPERTY_TYPE:
            if filter_item.operator == 'ILIKE_OR':
                conditions = []
                for synonym in filter_item.value:
                    conditions.extend([
                        f"property_type ILIKE '%{synonym}%'",
                        f"property_subtype ILIKE '%{synonym}%'"
                    ])
                return f"({' OR '.join(conditions)})"
        
        elif filter_item.filter_type == FilterType.PRICE:
            if filter_item.operator == '<=':
                return f"asking_price <= {filter_item.value}"
```

### Step 6: Enhanced SQL Integration
**File: `backend/enhanced_sql_integration.py`**
```python
class EnhancedSQLGenerator:
    def generate_and_validate_sql(self, user_query: str, gpt4_generated_query: str) -> Dict[str, Any]:
        """Main integration point - processes queries through the feedback loop"""
        
        # Process through feedback loop
        feedback_result = self.feedback_loop.process_query(user_query, gpt4_generated_query)
        
        # Prepare enhanced response
        enhanced_response = {
            'original_query': gpt4_generated_query,
            'final_sql': feedback_result['final_query'],
            'results': feedback_result['result'],
            'validation_status': feedback_result['validation_status'].value,
            'was_corrected': feedback_result['validation_status'] == ValidationStatus.CORRECTED,
            'iteration_count': feedback_result['iteration_count'],
            'explanation': feedback_result['explanation'],
            'correction_history': feedback_result['correction_history'],
            'constraints': asdict(feedback_result['constraints']),
            'metadata': {
                'execution_time': feedback_result['result'].execution_time,
                'row_count': feedback_result['result'].row_count,
                'columns': feedback_result['result'].columns,
                'errors': feedback_result['result'].errors,
                'warnings': feedback_result['result'].warnings
            }
        }
        
        return enhanced_response
```

---

## Self-Feedback Loop System

### How the Self-Correction System Works

### Step 1: Query Processing Entry Point
**File: `backend/sql_feedback_loop.py`**
```python
class SQLFeedbackLoop:
    def process_query(self, user_input: str, gpt4_generated_query: str) -> Dict[str, Any]:
        """Main processing function that implements the feedback loop"""
        
        # Step 1: Extract constraints from user input
        constraints = self.constraint_extractor.extract_constraints(user_input)
        
        # Step 2: Initialize variables
        current_query = gpt4_generated_query
        iteration_count = 0
        validation_status = ValidationStatus.SUCCESS
        correction_history = []
        
        # Step 3: Feedback loop (max 3 iterations)
        while iteration_count < self.max_iterations:
            iteration_count += 1
            
            # Execute current query
            result = self._execute_query(current_query)
            
            # Validate results
            is_valid, issues = self.query_validator.validate_results(result, constraints, current_query)
            
            if is_valid:
                break
            
            # Generate correction
            corrected_query, correction_reason = self.sql_corrector.generate_correction(
                current_query, constraints, issues, user_input
            )
            
            if corrected_query == current_query:
                validation_status = ValidationStatus.FAILED
                break
            
            # Store correction history
            correction_history.append({
                'iteration': iteration_count,
                'issues': issues,
                'correction_reason': correction_reason,
                'original_query': current_query,
                'corrected_query': corrected_query
            })
            
            current_query = corrected_query
            validation_status = ValidationStatus.CORRECTED
        
        # Step 4: Execute final query and store learning
        final_result = self._execute_query(current_query)
        self._store_learning_record(user_input, gpt4_generated_query, current_query, constraints, correction_history, iteration_count, validation_status)
        
        return {
            'final_query': current_query,
            'result': final_result,
            'validation_status': validation_status,
            'iteration_count': iteration_count,
            'correction_history': correction_history,
            'constraints': constraints,
            'explanation': self._generate_explanation(correction_history, validation_status)
        }
```

### Step 2: Constraint Extraction
**File: `backend/sql_feedback_loop.py`**
```python
class ConstraintExtractor:
    def extract_constraints(self, user_query: str) -> QueryConstraints:
        """Extract constraints from natural language query"""
        query_lower = user_query.lower()
        
        # Extract counties
        counties = []
        for county in self.schema_mapper.COUNTY_MAPPINGS.keys():
            if county in query_lower:
                counties.append(county)
        
        # Extract price ranges
        price_range = self._extract_price_range(query_lower)
        
        # Extract property types
        property_types = []
        for prop_type in self.schema_mapper.PROPERTY_TYPE_MAPPINGS.keys():
            if prop_type in query_lower:
                property_types.append(prop_type)
        
        # Extract aggregation type
        aggregation_type = self._extract_aggregation(query_lower)
        
        # Set expected result ranges
        expected_min, expected_max = self._estimate_result_count(counties, property_types, aggregation_type, query_lower)
        
        return QueryConstraints(
            counties=counties,
            price_range=price_range,
            size_range=size_range,
            property_types=property_types,
            aggregation_type=aggregation_type,
            order_by=order_by,
            limit=limit,
            filters=filters,
            expected_min_results=expected_min,
            expected_max_results=expected_max
        )
```

### Step 3: Query Validation
**File: `backend/sql_feedback_loop.py`**
```python
class QueryValidator:
    def validate_results(self, result: QueryResult, constraints: QueryConstraints, original_query: str) -> Tuple[bool, List[str]]:
        """Validate query results against constraints"""
        issues = []
        
        # Check result count
        if result.row_count < constraints.expected_min_results:
            issues.append(f"Too few results: got {result.row_count}, expected at least {constraints.expected_min_results}")
        
        if (constraints.expected_max_results and result.row_count > constraints.expected_max_results):
            issues.append(f"Too many results: got {result.row_count}, expected at most {constraints.expected_max_results}")
        
        # Check for SQL errors
        if result.errors:
            issues.extend(result.errors)
        
        # Validate county filtering
        if constraints.counties and not self._validate_county_filter(original_query, constraints.counties):
            issues.append("County filter appears incorrect in SQL")
        
        # Validate price range
        if constraints.price_range and not self._validate_price_range(original_query, constraints.price_range):
            issues.append("Price range filter appears incorrect in SQL")
        
        return len(issues) == 0, issues
```

### Step 4: SQL Correction
**File: `backend/sql_feedback_loop.py`**
```python
class SQLCorrector:
    def generate_correction(self, original_query: str, constraints: QueryConstraints, issues: List[str], user_input: str) -> Tuple[str, str]:
        """Generate corrected SQL query"""
        corrected_query = original_query
        corrections_applied = []
        
        # Apply county corrections
        if any("County filter appears incorrect" in issue for issue in issues):
            corrected_query, county_corrections = self._fix_county_filters(corrected_query, constraints.counties)
            corrections_applied.extend(county_corrections)
        
        # Apply aggregation corrections
        if any("Aggregation query validation failed" in issue for issue in issues):
            corrected_query, agg_corrections = self._fix_aggregation_query(corrected_query, constraints)
            corrections_applied.extend(agg_corrections)
        
        # Apply result count corrections
        if any("Too few results" in issue for issue in issues):
            corrected_query, count_corrections = self._fix_low_results(corrected_query, constraints)
            corrections_applied.extend(count_corrections)
        
        # Learn from similar corrections
        similar_corrections = self.learning_store.get_similar_corrections(constraints)
        if similar_corrections:
            corrected_query, learned_corrections = self._apply_learned_patterns(corrected_query, similar_corrections, constraints)
            corrections_applied.extend(learned_corrections)
        
        correction_reason = "; ".join(corrections_applied) if corrections_applied else "No specific corrections applied"
        
        return corrected_query, correction_reason
    
    def _fix_county_filters(self, query: str, counties: List[str]) -> Tuple[str, List[str]]:
        """Fix incorrect county filtering"""
        corrections = []
        corrected_query = query
        
        for county in counties:
            # Replace property_type county searches with address searches
            old_pattern = f"property_type ILIKE '%{county}%'"
            new_pattern = f"address->>'county' ILIKE '%{county}%'"
            
            if old_pattern in query:
                corrected_query = corrected_query.replace(old_pattern, new_pattern)
                corrections.append(f"Fixed {county} county filter to use address field")
        
        return corrected_query, corrections
```

### Step 5: Learning Storage
**File: `backend/sql_feedback_loop.py`**
```python
class LearningStore:
    def store_feedback(self, record: FeedbackRecord):
        """Store feedback record for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO feedback_records 
                (query_hash, original_query, corrected_query, user_input, 
                 constraints, correction_reason, timestamp, iteration_count, 
                 validation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.query_hash,
                record.original_query,
                record.corrected_query,
                record.user_input,
                json.dumps(asdict(record.constraints)),
                record.correction_reason,
                record.timestamp.isoformat(),
                record.iteration_count,
                record.validation_status.value
            ))
            conn.commit()
        finally:
            conn.close()
```

---

## Address Analysis Flow

### Scenario: User enters address in Address Details Mode

### Step 1: Address Input
**File: `frontend/src/components/Chatbot/AddressDetailsMode.jsx`**
```javascript
const AddressDetailsMode = () => {
  const [address, setAddress] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyzeAddress = async () => {
    if (!address.trim()) return;

    setLoading(true);
    try {
      const response = await fetchAddressDetails(address);
      setAnalysis(response);
    } catch (error) {
      console.error('Address analysis error:', error);
    } finally {
      setLoading(false);
    }
  };
};
```

### Step 2: Address Analysis API Call
**File: `frontend/src/services/api.js`**
```javascript
export const fetchAddressDetails = async (address) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/address-analysis`, { address });
    return response.data;
  } catch (error) {
    console.error('Error fetching address details:', error);
    throw error;
  }
};
```

### Step 3: Backend Address Analysis Endpoint
**File: `backend/api.py`**
```python
@app.post("/address-analysis", response_model=AddressAnalysisResponse)
async def analyze_address(request: AddressRequest):
    """Analyze address using Smarty US Address Enrichment API"""
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
```

### Step 4: Smarty Address Analyzer
**File: `backend/smarty_address_analyzer_new.py`**
```python
class SmartyAddressAnalyzer:
    def analyze_address(self, address: str) -> Dict[str, Any]:
        """Main method to analyze an address and return comprehensive results"""
        try:
            # Step 1: Validate the address
            validated_address = self._validate_address(address)
            if not validated_address:
                return self._create_error_response(address, "Address validation failed")
            
            # Step 2: Get enrichment data from Smarty API
            property_data = self._get_property_data(address)
            risk_data = self._get_risk_data(address)
            
            # Step 3: Parse the response data
            parsed_data = self._parse_smarty_response(property_data, risk_data, address)
            
            # Step 4: Extract address components
            matched_address = validated_address.get('matched_address', {})
            
            return {
                "formatted_address": f"{matched_address.get('street', '')} {matched_address.get('city', '')} {matched_address.get('state', '')} {matched_address.get('zipcode', '')}".strip(),
                "city": matched_address.get('city', ''),
                "state": matched_address.get('state', ''),
                "zip_code": matched_address.get('zipcode', ''),
                "county": parsed_data.get('location_info', {}).get('county', ''),
                "property_info": parsed_data.get('property_info', {}),
                "financial_info": parsed_data.get('financial_info', {}),
                "investment_analysis": {
                    "investment_score": parsed_data.get('investment_score', 0),
                    "analysis": self._format_analysis_results(address, parsed_data)
                }
            }
            
        except Exception as e:
            return self._create_error_response(address, str(e))
    
    def _validate_address(self, address: str) -> Optional[Dict]:
        """Validate address using property lookup"""
        try:
            url = f"{self.base_url}/lookup/search/property/principal"
            params = {
                "freeform": address,
                "auth-id": self.auth_id,
                "auth-token": self.auth_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except Exception as e:
            self.logger.error(f"Address validation error: {str(e)}")
            return None
    
    def _get_property_data(self, address: str) -> Optional[Dict]:
        """Get property enrichment data from Smarty API"""
        try:
            url = f"{self.base_url}/lookup/search/property/principal"
            params = {
                "freeform": address,
                "auth-id": self.auth_id,
                "auth-token": self.auth_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data[0] if data else None
            
        except Exception as e:
            self.logger.error(f"Property data error: {str(e)}")
            return None
```

---

## Database Schema and Queries

### Database Structure
**Table: "Georgia Properties"**
```sql
CREATE TABLE "Georgia Properties" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    property_type VARCHAR(100),
    property_subtype VARCHAR(100),
    asking_price DECIMAL(15,2),
    address JSONB,
    size_acres DECIMAL(10,2),
    size_sqft INTEGER,
    building_sqft INTEGER,
    thumbnail_url VARCHAR(500),
    status VARCHAR(50),
    listing_url VARCHAR(500),
    zoning VARCHAR(100),
    traffic_count_aadt INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Queries Generated by the System

#### 1. Gas Stations Under $500k
```sql
SELECT id, name, property_type, property_subtype, asking_price, 
       address, listing_url, zoning, size_acres
FROM "Georgia Properties" 
WHERE (property_type ILIKE '%gas%' OR property_subtype ILIKE '%station%' 
       OR property_type ILIKE '%gasoline%' OR property_subtype ILIKE '%fuel%')
  AND asking_price <= 500000
ORDER BY asking_price ASC
LIMIT 50
```

#### 2. County Count Aggregation
```sql
SELECT address->>'county' AS county, COUNT(*) AS property_count
FROM "Georgia Properties"
WHERE address->>'county' IS NOT NULL
GROUP BY address->>'county'
ORDER BY property_count DESC
```

#### 3. Properties in Specific County
```sql
SELECT id, name, property_type, asking_price, address, size_acres
FROM "Georgia Properties" 
WHERE address->>'county' ILIKE '%walton%'
ORDER BY asking_price ASC
LIMIT 50
```

---

## Error Handling and Validation

### Frontend Error Handling
**File: `frontend/src/components/Chatbot/QueryMode.jsx`**
```javascript
const handleSendQuery = async () => {
  try {
    const response = await sendMessage(query);
    // Process successful response
  } catch (error) {
    console.error('Chat error:', error);
    const errorMessage = { 
      type: 'bot', 
      content: `❌ Sorry, I encountered an error processing your request. Please make sure the backend server is running and try again.\n\nError: ${error.message}` 
    };
    setMessages(prev => [...prev, errorMessage]);
  } finally {
    setIsLoading(false);
  }
};
```

### Backend Error Handling
**File: `backend/api.py`**
```python
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Process query
        result = enhanced_generator.generate_and_validate_sql(user_query, gpt4_query)
        # Return success response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
```

### SQL Execution Error Handling
**File: `backend/sql_feedback_loop.py`**
```python
def _execute_query(self, query: str) -> QueryResult:
    """Execute SQL query and return structured result"""
    start_time = datetime.now()
    errors = []
    warnings = []
    
    try:
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys()) if hasattr(result, 'keys') else []
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return QueryResult(
                rows=rows,
                row_count=len(rows),
                columns=columns,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings
            )
    
    except SQLAlchemyError as e:
        errors.append(str(e))
        logger.error(f"SQL execution error: {e}")
        
        return QueryResult(
            rows=[],
            row_count=0,
            columns=[],
            execution_time=(datetime.now() - start_time).total_seconds(),
            errors=errors,
            warnings=warnings
        )
```

---

## API Endpoints Reference

### 1. Chat Endpoint
```
POST /chat
Content-Type: application/json

Request Body:
{
  "message": "Show me gas stations under $500k"
}

Response:
{
  "response": "Found 15 properties matching your search.",
  "sql_query": "SELECT id, name, property_type, asking_price...",
  "properties": [...],
  "validation_status": "success",
  "was_corrected": false,
  "correction_explanation": null
}
```

### 2. Properties Endpoint
```
GET /properties?page=1&limit=20&property_type=retail&min_price=100000&max_price=500000

Response:
{
  "properties": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 100,
    "has_next": true,
    "has_prev": false
  }
}
```

### 3. Address Analysis Endpoint
```
POST /address-analysis
Content-Type: application/json

Request Body:
{
  "address": "123 Main St, Atlanta, GA 30309"
}

Response:
{
  "formatted_address": "123 Main St Atlanta GA 30309",
  "city": "Atlanta",
  "state": "GA",
  "zip_code": "30309",
  "county": "Fulton",
  "property_info": {...},
  "financial_info": {...},
  "investment_analysis": {...}
}
```

---

## Code File Dependencies

### Frontend Dependencies
```
App.jsx
├── ThemeContext.tsx
├── Header.jsx
├── Sidebar.jsx
└── Pages/
    ├── ChatPage.jsx
    │   ├── Chatbot.jsx
    │   │   ├── QueryMode.jsx
    │   │   │   ├── chatService.js
    │   │   │   └── api.js
    │   │   └── AddressDetailsMode.jsx
    │   └── PropertyCard.tsx
    └── PropertiesPage.jsx
        ├── PropertyGallery.tsx
        └── api.js
```

### Backend Dependencies
```
api.py (Main FastAPI Server)
├── enhanced_sql_integration.py
│   ├── query_parser.py
│   │   └── SQLGenerator class
│   └── sql_feedback_loop.py
│       ├── ConstraintExtractor
│       ├── QueryValidator
│       ├── SQLCorrector
│       └── LearningStore
├── smarty_address_analyzer_new.py
└── config.py
    └── Environment variables
```

### External Dependencies
```
OpenAI API (GPT-4)
├── LlamaIndex integration
└── Natural language processing

Smarty Streets API
├── Address validation
├── Property enrichment
└── Financial data

PostgreSQL Database
├── Georgia Properties table
└── JSONB address data

Crexi Integration
└── Property listing links
```

---

## Configuration and Environment

### Frontend Environment Variables
```bash
# .env.local
REACT_APP_API_URL=http://localhost:8003
```

### Backend Environment Variables
```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database
SMARTY_AUTH_ID=your_smarty_auth_id
SMARTY_AUTH_TOKEN=your_smarty_auth_token
```

### Database Configuration
```python
# backend/config.py
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMARTY_AUTH_ID = os.getenv("SMARTY_AUTH_ID")
SMARTY_AUTH_TOKEN = os.getenv("SMARTY_AUTH_TOKEN")
```

---

This documentation provides a complete technical overview of how every request flows through the MIPA system, from frontend user interaction to backend processing and database queries. Each component is explained with code examples and detailed flow descriptions.
