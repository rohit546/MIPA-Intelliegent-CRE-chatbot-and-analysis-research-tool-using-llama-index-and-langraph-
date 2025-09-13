"""
Self-Correcting SQL Query Module with Feedback Loop
Backend implementation for intelligent query validation and learning
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    SUCCESS = "success"
    CORRECTED = "corrected"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"

@dataclass
class QueryConstraints:
    """Extracted constraints from natural language query"""
    counties: List[str]
    price_range: Optional[Tuple[float, float]]
    size_range: Optional[Tuple[float, float]]
    property_types: List[str]
    aggregation_type: Optional[str]  # COUNT, SUM, AVG, etc.
    order_by: Optional[str]
    limit: Optional[int]
    filters: Dict[str, Any]
    expected_min_results: int = 0
    expected_max_results: Optional[int] = None

@dataclass
class QueryResult:
    """Result of SQL execution with metadata"""
    rows: List[Tuple]
    row_count: int
    columns: List[str]
    execution_time: float
    errors: List[str]
    warnings: List[str]

@dataclass
class FeedbackRecord:
    """Record of query correction for learning"""
    query_hash: str
    original_query: str
    corrected_query: str
    user_input: str
    constraints: QueryConstraints
    correction_reason: str
    timestamp: datetime
    iteration_count: int
    validation_status: ValidationStatus

class SchemaMapper:
    """Maps natural language concepts to database schema"""
    
    COUNTY_MAPPINGS = {
        'dekalb': "address->>'county' ILIKE '%dekalb%'",
        'fulton': "address->>'county' ILIKE '%fulton%'",
        'gwinnett': "address->>'county' ILIKE '%gwinnett%'",
        'walton': "address->>'county' ILIKE '%walton%'",
        'cobb': "address->>'county' ILIKE '%cobb%'",
        'clayton': "address->>'county' ILIKE '%clayton%'",
        'henry': "address->>'county' ILIKE '%henry%'",
        'douglas': "address->>'county' ILIKE '%douglas%'",
        'rockdale': "address->>'county' ILIKE '%rockdale%'"
    }
    
    PROPERTY_TYPE_MAPPINGS = {
        'gas station': "(property_type ILIKE '%gas%' OR property_subtype ILIKE '%station%')",
        'retail': "(property_type ILIKE '%retail%' OR property_subtype ILIKE '%retail%')",
        'restaurant': "(property_type ILIKE '%restaurant%' OR property_subtype ILIKE '%dining%')",
        'vacant': "(property_type ILIKE '%vacant%' OR status ILIKE '%vacant%')",
        'commercial': "(property_type ILIKE '%commercial%' OR property_subtype ILIKE '%commercial%')"
    }
    
    SIZE_COLUMN_MAPPINGS = {
        'acres': 'size_acres',
        'square feet': 'size_sqft',
        'building size': 'building_sqft',
        'lot size': 'size_sqft'
    }

class ConstraintExtractor:
    """Extracts structured constraints from natural language"""
    
    def __init__(self):
        self.schema_mapper = SchemaMapper()
    
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
        
        # Extract size ranges
        size_range = self._extract_size_range(query_lower)
        
        # Extract property types
        property_types = []
        for prop_type in self.schema_mapper.PROPERTY_TYPE_MAPPINGS.keys():
            if prop_type in query_lower:
                property_types.append(prop_type)
        
        # Extract aggregation type
        aggregation_type = self._extract_aggregation(query_lower)
        
        # Extract ordering
        order_by = self._extract_order_by(query_lower)
        
        # Extract limit
        limit = self._extract_limit(query_lower)
        
        # Extract additional filters
        filters = self._extract_additional_filters(query_lower)
        
        # Set expected result ranges based on query type
        expected_min, expected_max = self._estimate_result_count(
            counties, property_types, aggregation_type, query_lower
        )
        
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
    
    def _extract_price_range(self, query: str) -> Optional[Tuple[float, float]]:
        """Extract price range from query"""
        # Pattern for "between $X and $Y"
        between_pattern = r'between\s*\$?([\d,]+)k?\s*and\s*\$?([\d,]+)k?'
        match = re.search(between_pattern, query)
        if match:
            min_price = float(match.group(1).replace(',', ''))
            max_price = float(match.group(2).replace(',', ''))
            if 'k' in match.group(0):
                min_price *= 1000
                max_price *= 1000
            return (min_price, max_price)
        
        # Pattern for "under $X"
        under_pattern = r'under\s*\$?([\d,]+)k?'
        match = re.search(under_pattern, query)
        if match:
            max_price = float(match.group(1).replace(',', ''))
            if 'k' in match.group(0):
                max_price *= 1000
            return (0, max_price)
        
        # Pattern for "over $X"
        over_pattern = r'over\s*\$?([\d,]+)k?'
        match = re.search(over_pattern, query)
        if match:
            min_price = float(match.group(1).replace(',', ''))
            if 'k' in match.group(0):
                min_price *= 1000
            return (min_price, float('inf'))
        
        return None
    
    def _extract_size_range(self, query: str) -> Optional[Tuple[float, float]]:
        """Extract size range from query"""
        # Pattern for "X to Y acres"
        range_pattern = r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*acres?'
        match = re.search(range_pattern, query)
        if match:
            return (float(match.group(1)), float(match.group(2)))
        
        # Pattern for "over X acres"
        over_pattern = r'over\s*(\d+(?:\.\d+)?)\s*acres?'
        match = re.search(over_pattern, query)
        if match:
            return (float(match.group(1)), float('inf'))
        
        # Pattern for "X acres" (exact)
        exact_pattern = r'(\d+(?:\.\d+)?)\s*acres?'
        match = re.search(exact_pattern, query)
        if match and 'to' not in query and 'over' not in query:
            size = float(match.group(1))
            return (size, size)
        
        return None
    
    def _extract_aggregation(self, query: str) -> Optional[str]:
        """Extract aggregation type from query"""
        if any(word in query for word in ['how many', 'count', 'number of']):
            return 'COUNT'
        elif 'average' in query or 'avg' in query:
            return 'AVG'
        elif 'sum' in query or 'total' in query:
            return 'SUM'
        elif 'maximum' in query or 'max' in query:
            return 'MAX'
        elif 'minimum' in query or 'min' in query:
            return 'MIN'
        return None
    
    def _extract_order_by(self, query: str) -> Optional[str]:
        """Extract ordering preference from query"""
        if 'cheapest' in query or 'lowest price' in query:
            return 'asking_price ASC'
        elif 'expensive' in query or 'highest price' in query:
            return 'asking_price DESC'
        elif 'largest' in query or 'biggest' in query:
            return 'size_acres DESC'
        elif 'smallest' in query:
            return 'size_acres ASC'
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract limit from query"""
        # Pattern for "first X", "top X", "X properties"
        limit_patterns = [
            r'first\s+(\d+)',
            r'top\s+(\d+)',
            r'(\d+)\s+properties',
            r'limit\s+(\d+)'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_additional_filters(self, query: str) -> Dict[str, Any]:
        """Extract additional filters"""
        filters = {}
        
        if 'vacant' in query:
            filters['status'] = 'Vacant'
        
        if 'available' in query:
            filters['status'] = 'Available'
        
        if 'traffic' in query:
            filters['has_traffic_data'] = True
        
        if 'income' in query:
            filters['has_income_data'] = True
        
        return filters
    
    def _estimate_result_count(self, counties: List[str], property_types: List[str], 
                             aggregation_type: Optional[str], query: str) -> Tuple[int, Optional[int]]:
        """Estimate expected result count based on constraints"""
        if aggregation_type:
            # Aggregation queries should return fewer results
            if 'counties' in query:
                return (1, 20)  # Number of counties
            else:
                return (1, 1)   # Single aggregation result
        
        # Regular queries
        if counties and property_types:
            return (1, 100)  # Specific filters
        elif counties or property_types:
            return (5, 500)  # Some filters
        else:
            return (10, 1000)  # Broad query

class QueryValidator:
    """Validates SQL query results against expected constraints"""
    
    def __init__(self, schema_mapper: SchemaMapper):
        self.schema_mapper = schema_mapper
    
    def validate_results(self, result: QueryResult, constraints: QueryConstraints, 
                        original_query: str) -> Tuple[bool, List[str]]:
        """Validate query results against constraints"""
        issues = []
        
        # Check result count
        if result.row_count < constraints.expected_min_results:
            issues.append(f"Too few results: got {result.row_count}, expected at least {constraints.expected_min_results}")
        
        if (constraints.expected_max_results and 
            result.row_count > constraints.expected_max_results):
            issues.append(f"Too many results: got {result.row_count}, expected at most {constraints.expected_max_results}")
        
        # Check for SQL errors
        if result.errors:
            issues.extend(result.errors)
        
        # Validate aggregation queries
        if constraints.aggregation_type:
            if not self._validate_aggregation(result, constraints, original_query):
                issues.append("Aggregation query validation failed")
        
        # Validate county filtering
        if constraints.counties and not self._validate_county_filter(original_query, constraints.counties):
            issues.append("County filter appears incorrect in SQL")
        
        # Validate price range
        if constraints.price_range and not self._validate_price_range(original_query, constraints.price_range):
            issues.append("Price range filter appears incorrect in SQL")
        
        return len(issues) == 0, issues
    
    def _validate_aggregation(self, result: QueryResult, constraints: QueryConstraints, 
                            query: str) -> bool:
        """Validate aggregation queries"""
        query_upper = query.upper()
        
        if constraints.aggregation_type == 'COUNT':
            # COUNT queries should have COUNT() in SELECT
            if 'COUNT(' not in query_upper:
                return False
            # Should have reasonable result count
            if result.row_count == 0:
                return False
        
        return True
    
    def _validate_county_filter(self, query: str, counties: List[str]) -> bool:
        """Validate county filtering in SQL"""
        query_lower = query.lower()
        
        for county in counties:
            # Check if county is properly filtered using address field
            if county in query_lower:
                if f"address->>'county'" in query_lower or "address::text" in query_lower:
                    continue
                elif f"property_type ilike '%{county}%'" in query_lower:
                    # Wrong field used for county
                    return False
        
        return True
    
    def _validate_price_range(self, query: str, price_range: Tuple[float, float]) -> bool:
        """Validate price range filtering"""
        query_lower = query.lower()
        min_price, max_price = price_range
        
        # Should have asking_price in WHERE clause
        if 'asking_price' not in query_lower:
            return False
        
        # Check for BETWEEN clause if both bounds exist
        if min_price > 0 and max_price < float('inf'):
            if 'between' not in query_lower:
                return False
        
        return True

class LearningStore:
    """Stores and retrieves learning data for query corrections"""
    
    def __init__(self, db_path: str = "query_learning.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for learning storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                original_query TEXT,
                corrected_query TEXT,
                user_input TEXT,
                constraints TEXT,
                correction_reason TEXT,
                timestamp TEXT,
                iteration_count INTEGER,
                validation_status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_hash 
            ON feedback_records(query_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def store_feedback(self, record: FeedbackRecord):
        """Store feedback record"""
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
            logger.info(f"Stored feedback record for query hash: {record.query_hash}")
        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
        finally:
            conn.close()
    
    def get_similar_corrections(self, constraints: QueryConstraints, limit: int = 5) -> List[FeedbackRecord]:
        """Retrieve similar correction patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Simple similarity based on constraint matching
            cursor.execute("""
                SELECT * FROM feedback_records 
                WHERE validation_status = 'corrected'
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            records = []
            for row in cursor.fetchall():
                record = FeedbackRecord(
                    query_hash=row[1],
                    original_query=row[2],
                    corrected_query=row[3],
                    user_input=row[4],
                    constraints=QueryConstraints(**json.loads(row[5])),
                    correction_reason=row[6],
                    timestamp=datetime.fromisoformat(row[7]),
                    iteration_count=row[8],
                    validation_status=ValidationStatus(row[9])
                )
                records.append(record)
            
            return records
        except Exception as e:
            logger.error(f"Error retrieving similar corrections: {e}")
            return []
        finally:
            conn.close()

class SQLCorrector:
    """Generates corrected SQL queries based on validation issues"""
    
    def __init__(self, schema_mapper: SchemaMapper, learning_store: LearningStore):
        self.schema_mapper = schema_mapper
        self.learning_store = learning_store
    
    def generate_correction(self, original_query: str, constraints: QueryConstraints, 
                          issues: List[str], user_input: str) -> Tuple[str, str]:
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
        
        # Apply price range corrections
        if any("Price range filter appears incorrect" in issue for issue in issues):
            corrected_query, price_corrections = self._fix_price_range(corrected_query, constraints.price_range)
            corrections_applied.extend(price_corrections)
        
        # Ensure essential columns are included
        corrected_query, column_corrections = self._ensure_essential_columns(corrected_query)
        corrections_applied.extend(column_corrections)
        
        # Learn from similar corrections
        similar_corrections = self.learning_store.get_similar_corrections(constraints)
        if similar_corrections:
            corrected_query, learned_corrections = self._apply_learned_patterns(
                corrected_query, similar_corrections, constraints
            )
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
    
    def _fix_aggregation_query(self, query: str, constraints: QueryConstraints) -> Tuple[str, List[str]]:
        """Fix aggregation query issues"""
        corrections = []
        corrected_query = query
        
        if constraints.aggregation_type == 'COUNT':
            if 'COUNT(' not in query.upper():
                # Add COUNT to SELECT
                if 'SELECT ' in query:
                    corrected_query = query.replace('SELECT ', 'SELECT COUNT(*), ')
                    corrections.append("Added COUNT(*) to aggregation query")
            
            # Remove asking_price from GROUP BY if present
            if 'GROUP BY' in query.upper() and 'asking_price' in query:
                corrected_query = re.sub(r',\s*asking_price', '', corrected_query)
                corrections.append("Removed asking_price from GROUP BY clause")
        
        return corrected_query, corrections
    
    def _fix_low_results(self, query: str, constraints: QueryConstraints) -> Tuple[str, List[str]]:
        """Fix queries returning too few results"""
        corrections = []
        corrected_query = query
        
        # Broaden property type searches
        if constraints.property_types:
            for prop_type in constraints.property_types:
                if prop_type in self.schema_mapper.PROPERTY_TYPE_MAPPINGS:
                    old_pattern = f"property_type ILIKE '%{prop_type}%'"
                    new_pattern = self.schema_mapper.PROPERTY_TYPE_MAPPINGS[prop_type]
                    
                    if old_pattern in corrected_query:
                        corrected_query = corrected_query.replace(old_pattern, new_pattern)
                        corrections.append(f"Broadened {prop_type} search to include subtypes")
        
        return corrected_query, corrections
    
    def _fix_price_range(self, query: str, price_range: Optional[Tuple[float, float]]) -> Tuple[str, List[str]]:
        """Fix price range filtering"""
        corrections = []
        corrected_query = query
        
        if price_range:
            min_price, max_price = price_range
            
            # Add BETWEEN clause if missing
            if 'asking_price' in query.lower() and 'between' not in query.lower():
                if min_price > 0 and max_price < float('inf'):
                    # Replace > AND < with BETWEEN
                    range_pattern = r'asking_price\s*>\s*[\d.]+\s*AND\s*asking_price\s*<\s*[\d.]+'
                    if re.search(range_pattern, query, re.IGNORECASE):
                        new_clause = f"asking_price BETWEEN {min_price} AND {max_price}"
                        corrected_query = re.sub(range_pattern, new_clause, corrected_query, flags=re.IGNORECASE)
                        corrections.append("Converted price range to BETWEEN clause")
        
        return corrected_query, corrections
    
    def _ensure_essential_columns(self, query: str) -> Tuple[str, List[str]]:
        """Ensure essential columns are included in SELECT for proper display"""
        corrections = []
        corrected_query = query
        
        # Essential columns for proper display
        essential_columns = ['listing_url', 'address', 'zoning']
        
        # Check if it's an aggregation query (don't modify these)
        if any(keyword in query.upper() for keyword in ['GROUP BY', 'COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
            return corrected_query, corrections
        
        # Check if SELECT clause exists
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if not select_match:
            return corrected_query, corrections
        
        current_columns = select_match.group(1).strip()
        columns_to_add = []
        
        for col in essential_columns:
            if col not in current_columns.lower():
                columns_to_add.append(col)
        
        if columns_to_add:
            # Add missing essential columns
            new_columns = current_columns + ', ' + ', '.join(columns_to_add)
            corrected_query = corrected_query.replace(select_match.group(1), new_columns)
            corrections.append(f"Added essential display columns: {', '.join(columns_to_add)}")
        
        return corrected_query, corrections
    
    def _apply_learned_patterns(self, query: str, similar_corrections: List[FeedbackRecord], 
                              constraints: QueryConstraints) -> Tuple[str, List[str]]:
        """Apply learned correction patterns"""
        corrections = []
        corrected_query = query
        
        # Apply most common correction patterns
        for record in similar_corrections[:2]:  # Use top 2 similar corrections
            if record.correction_reason and "county filter" in record.correction_reason.lower():
                # Apply county correction pattern
                if constraints.counties:
                    for county in constraints.counties:
                        old_pattern = f"property_type ILIKE '%{county}%'"
                        new_pattern = f"address->>'county' ILIKE '%{county}%'"
                        if old_pattern in corrected_query:
                            corrected_query = corrected_query.replace(old_pattern, new_pattern)
                            corrections.append(f"Applied learned county correction pattern")
                            break
        
        return corrected_query, corrections

class SQLFeedbackLoop:
    """Main feedback loop orchestrator"""
    
    def __init__(self, database_url: str, max_iterations: int = 3):
        self.database_url = database_url
        self.max_iterations = max_iterations
        
        self.engine = create_engine(database_url)
        self.constraint_extractor = ConstraintExtractor()
        self.schema_mapper = SchemaMapper()
        self.query_validator = QueryValidator(self.schema_mapper)
        self.learning_store = LearningStore()
        self.sql_corrector = SQLCorrector(self.schema_mapper, self.learning_store)
        
        logger.info("SQLFeedbackLoop initialized")
    
    def process_query(self, user_input: str, gpt4_generated_query: str) -> Dict[str, Any]:
        """
        Main processing function that implements the feedback loop
        
        Args:
            user_input: Natural language query from user
            gpt4_generated_query: Initial SQL generated by GPT-4
            
        Returns:
            Dict containing final query, results, validation status, and metadata
        """
        logger.info(f"Processing query: {user_input[:100]}...")
        
        # Extract constraints from user input
        constraints = self.constraint_extractor.extract_constraints(user_input)
        logger.info(f"Extracted constraints: {constraints}")
        
        # Initialize variables
        current_query = gpt4_generated_query
        iteration_count = 0
        validation_status = ValidationStatus.SUCCESS
        correction_history = []
        
        while iteration_count < self.max_iterations:
            iteration_count += 1
            logger.info(f"Iteration {iteration_count}: Executing query")
            
            # Execute current query
            result = self._execute_query(current_query)
            
            # Validate results
            is_valid, issues = self.query_validator.validate_results(result, constraints, current_query)
            
            if is_valid:
                logger.info("Query validation successful")
                break
            
            # Log issues and attempt correction
            logger.warning(f"Validation issues: {issues}")
            
            # Generate correction
            corrected_query, correction_reason = self.sql_corrector.generate_correction(
                current_query, constraints, issues, user_input
            )
            
            if corrected_query == current_query:
                logger.warning("No corrections could be applied")
                validation_status = ValidationStatus.FAILED
                break
            
            correction_history.append({
                'iteration': iteration_count,
                'issues': issues,
                'correction_reason': correction_reason,
                'original_query': current_query,
                'corrected_query': corrected_query
            })
            
            current_query = corrected_query
            validation_status = ValidationStatus.CORRECTED
        
        if iteration_count >= self.max_iterations:
            validation_status = ValidationStatus.MAX_ITERATIONS
            logger.warning("Maximum iterations reached")
        
        # Execute final query
        final_result = self._execute_query(current_query)
        
        # Store learning record
        self._store_learning_record(
            user_input, gpt4_generated_query, current_query, constraints,
            correction_history, iteration_count, validation_status
        )
        
        return {
            'final_query': current_query,
            'result': final_result,
            'validation_status': validation_status,
            'iteration_count': iteration_count,
            'correction_history': correction_history,
            'constraints': constraints,
            'explanation': self._generate_explanation(correction_history, validation_status)
        }
    
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
    
    def _store_learning_record(self, user_input: str, original_query: str, final_query: str,
                             constraints: QueryConstraints, correction_history: List[Dict],
                             iteration_count: int, validation_status: ValidationStatus):
        """Store learning record for future improvements"""
        
        # Create query hash for deduplication
        query_hash = hashlib.md5(f"{user_input}:{original_query}".encode()).hexdigest()
        
        correction_reason = ""
        if correction_history:
            reasons = [item['correction_reason'] for item in correction_history]
            correction_reason = "; ".join(reasons)
        
        record = FeedbackRecord(
            query_hash=query_hash,
            original_query=original_query,
            corrected_query=final_query,
            user_input=user_input,
            constraints=constraints,
            correction_reason=correction_reason,
            timestamp=datetime.now(),
            iteration_count=iteration_count,
            validation_status=validation_status
        )
        
        self.learning_store.store_feedback(record)
    
    def _generate_explanation(self, correction_history: List[Dict], 
                            validation_status: ValidationStatus) -> str:
        """Generate human-readable explanation of corrections"""
        
        if validation_status == ValidationStatus.SUCCESS:
            return "Query executed successfully without corrections."
        
        if not correction_history:
            return "Query failed validation but no corrections could be applied."
        
        explanations = []
        for item in correction_history:
            explanations.append(f"Iteration {item['iteration']}: {item['correction_reason']}")
        
        status_msg = {
            ValidationStatus.CORRECTED: "Query was successfully corrected.",
            ValidationStatus.FAILED: "Query corrections failed.",
            ValidationStatus.MAX_ITERATIONS: "Maximum correction attempts reached."
        }.get(validation_status, "Unknown status")
        
        return f"{status_msg} Corrections applied: {'; '.join(explanations)}"
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning and corrections"""
        conn = sqlite3.connect(self.learning_store.db_path)
        cursor = conn.cursor()
        
        try:
            # Total records
            cursor.execute("SELECT COUNT(*) FROM feedback_records")
            total_records = cursor.fetchone()[0]
            
            # Status distribution
            cursor.execute("""
                SELECT validation_status, COUNT(*) 
                FROM feedback_records 
                GROUP BY validation_status
            """)
            status_dist = dict(cursor.fetchall())
            
            # Average iterations
            cursor.execute("SELECT AVG(iteration_count) FROM feedback_records")
            avg_iterations = cursor.fetchone()[0] or 0
            
            # Most common correction reasons
            cursor.execute("""
                SELECT correction_reason, COUNT(*) 
                FROM feedback_records 
                WHERE correction_reason != '' 
                GROUP BY correction_reason 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """)
            common_corrections = cursor.fetchall()
            
            return {
                'total_records': total_records,
                'status_distribution': status_dist,
                'average_iterations': round(avg_iterations, 2),
                'common_corrections': common_corrections
            }
        
        finally:
            conn.close()