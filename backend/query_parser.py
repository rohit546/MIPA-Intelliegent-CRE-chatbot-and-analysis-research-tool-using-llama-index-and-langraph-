"""
Advanced Query Parser for Natural Language to SQL conversion
Handles entity recognition, range parsing, and schema-aware filtering
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class FilterType(Enum):
    COUNTY = "county"
    CITY = "city"
    PROPERTY_TYPE = "property_type"
    STATUS = "status"
    SIZE_ACRES = "size_acres"
    SIZE_SQFT = "size_sqft"
    BUILDING_SQFT = "building_sqft"
    PRICE = "asking_price"
    TRAFFIC = "traffic_count_aadt"

@dataclass
class QueryFilter:
    filter_type: FilterType
    operator: str  # =, >, <, >=, <=, BETWEEN, ILIKE, IN
    value: Any
    value2: Optional[Any] = None  # For BETWEEN operations

@dataclass
class ParsedQuery:
    filters: List[QueryFilter]
    columns: List[str]
    order_by: Optional[Tuple[str, str]] = None  # (column, direction)
    limit: int = 50
    is_aggregate: bool = False
    aggregate_type: Optional[str] = None

class QueryParser:
    """Enhanced query parser with entity recognition and schema awareness"""
    
    # Georgia counties (comprehensive list)
    GEORGIA_COUNTIES = {
        'appling', 'atkinson', 'bacon', 'baker', 'baldwin', 'banks', 'barrow', 
        'bartow', 'ben hill', 'berrien', 'bibb', 'bleckley', 'brantley', 'brooks',
        'bryan', 'bulloch', 'burke', 'butts', 'calhoun', 'camden', 'candler',
        'carroll', 'catoosa', 'charlton', 'chatham', 'chattahoochee', 'chattooga',
        'cherokee', 'clarke', 'clay', 'clayton', 'clinch', 'cobb', 'coffee',
        'colquitt', 'columbia', 'cook', 'coweta', 'crawford', 'crisp', 'dade',
        'dawson', 'decatur', 'dekalb', 'de kalb', 'dodge', 'dooly', 'dougherty',
        'douglas', 'early', 'echols', 'effingham', 'elbert', 'emanuel', 'evans',
        'fannin', 'fayette', 'floyd', 'forsyth', 'franklin', 'fulton', 'gilmer',
        'glascock', 'glynn', 'gordon', 'grady', 'greene', 'gwinnett', 'habersham',
        'hall', 'hancock', 'haralson', 'harris', 'hart', 'heard', 'henry',
        'houston', 'irwin', 'jackson', 'jasper', 'jeff davis', 'jefferson',
        'jenkins', 'johnson', 'jones', 'lamar', 'lanier', 'laurens', 'lee',
        'liberty', 'lincoln', 'long', 'lowndes', 'lumpkin', 'macon', 'madison',
        'marion', 'mcduffie', 'mcintosh', 'meriwether', 'miller', 'mitchell',
        'monroe', 'montgomery', 'morgan', 'murray', 'muscogee', 'newton', 'oconee',
        'oglethorpe', 'paulding', 'peach', 'pickens', 'pierce', 'pike', 'polk',
        'pulaski', 'putnam', 'quitman', 'rabun', 'randolph', 'richmond', 'rockdale',
        'schley', 'screven', 'seminole', 'spalding', 'stephens', 'stewart',
        'sumter', 'talbot', 'taliaferro', 'tattnall', 'taylor', 'telfair',
        'terrell', 'thomas', 'tift', 'toombs', 'towns', 'treutlen', 'troup',
        'turner', 'twiggs', 'union', 'upson', 'walker', 'walton', 'ware',
        'warren', 'washington', 'wayne', 'webster', 'wheeler', 'white', 'whitfield',
        'wilcox', 'wilkes', 'wilkinson', 'worth'
    }
    
    # Property type synonyms with schema mapping
    PROPERTY_SYNONYMS = {
        # Gas stations
        'gas station': ['gas', 'gasoline', 'fuel', 'petrol', 'station'],
        'fuel station': ['gas', 'gasoline', 'fuel', 'petrol', 'station'],
        
        # Convenience stores
        'convenience store': ['convenience', 'c-store', 'corner', 'mini mart', 'quick mart'],
        'c-store': ['convenience', 'c-store', 'corner', 'mini mart', 'quick mart'],
        'corner store': ['convenience', 'c-store', 'corner', 'mini mart', 'quick mart'],
        
        # Food service
        'restaurant': ['restaurant', 'dining', 'food', 'eatery', 'qsr', 'fast food'],
        'fast food': ['restaurant', 'dining', 'food', 'eatery', 'qsr', 'fast food'],
        'qsr': ['restaurant', 'dining', 'food', 'eatery', 'qsr', 'fast food'],
        
        # Retail
        'retail': ['retail', 'store', 'shop', 'commercial'],
        'store': ['retail', 'store', 'shop', 'commercial'],
        
        # Office
        'office': ['office', 'professional', 'commercial office'],
        
        # Status mappings (special handling)
        'vacant': ['vacant', 'empty', 'available'],
        'for sale': ['sale', 'available', 'listed'],
        'sold': ['sold', 'closed', 'completed']
    }
    
    # Size unit patterns
    SIZE_PATTERNS = {
        'acres': r'(\d+(?:\.\d+)?)\s*(?:to|\-|and)\s*(\d+(?:\.\d+)?)\s*acres?',
        'acres_single': r'(\d+(?:\.\d+)?)\s*acres?',
        'sqft': r'(\d+(?:,\d+)?)\s*(?:sq\.?\s*ft\.?|square\s*feet?|sqft)',
        'sqft_range': r'(\d+(?:,\d+)?)\s*(?:to|\-|and)\s*(\d+(?:,\d+)?)\s*(?:sq\.?\s*ft\.?|square\s*feet?|sqft)'
    }
    
    # Price patterns
    PRICE_PATTERNS = {
        'under': r'under\s*\$?(\d+(?:,\d+)*(?:[km])?)',
        'over': r'over\s*\$?(\d+(?:,\d+)*(?:[km])?)',
        'between': r'between\s*\$?(\d+(?:,\d+)*(?:[km])?)\s*(?:and|to|\-)\s*\$?(\d+(?:,\d+)*(?:[km])?)',
        'exact': r'\$(\d+(?:,\d+)*(?:[km])?)'
    }

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset parser state for new query"""
        self.filters = []
        self.columns = ['id', 'name', 'property_type', 'property_subtype', 'asking_price']
        self.order_by = None
        self.limit = 50

    def parse(self, query: str) -> ParsedQuery:
        """Main parsing entry point"""
        self.reset()
        query_lower = query.lower().strip()
        
        # Check for aggregation queries first
        if self._is_aggregation_query(query_lower):
            return self._parse_aggregation_query(query_lower)
        
        # Parse different components for regular queries
        self._parse_location(query_lower)
        self._parse_property_type(query_lower)
        self._parse_status(query_lower)
        self._parse_size(query_lower)
        self._parse_price(query_lower)
        self._parse_ordering(query_lower)
        self._determine_columns()
        
        return ParsedQuery(
            filters=self.filters,
            columns=self.columns,
            order_by=self.order_by,
            limit=self.limit
        )
    
    def _is_aggregation_query(self, query: str) -> bool:
        """Check if this is an aggregation/statistics query"""
        aggregation_keywords = [
            'how many counties', 'county count', 'counties', 'count of counties',
            'count of every county', 'which county has how many',
            'how many properties', 'total properties', 'count all',
            'property types count', 'count by type', 'types statistics'
        ]
        return any(keyword in query for keyword in aggregation_keywords)
    
    def _parse_aggregation_query(self, query: str) -> ParsedQuery:
        """Handle aggregation/statistics queries"""
        self.reset()
        
        # County statistics
        if any(word in query for word in ['counties', 'county count', 'how many counties', 'count of counties', 'count of every county', 'which county has how many']):
            return ParsedQuery(
                filters=[],
                columns=['county', 'property_count'],
                order_by=('property_count', 'DESC'),
                limit=None,
                is_aggregate=True,
                aggregate_type='county_count'
            )
        
        # Property type count
        if any(word in query for word in ['count by type', 'property types count', 'types statistics']):
            return ParsedQuery(
                filters=[],
                columns=['property_type', 'property_count'],
                order_by=('property_count', 'DESC'),
                limit=None,
                is_aggregate=True,
                aggregate_type='type_count'
            )
        
        # Total count
        if any(word in query for word in ['total', 'count all', 'how many properties']):
            return ParsedQuery(
                filters=[],
                columns=['total_properties'],
                order_by=None,
                limit=None,
                is_aggregate=True,
                aggregate_type='total_count'
            )
        
        # Default to regular parsing if no specific aggregation found
        return self.parse(query)

    def _parse_location(self, query: str):
        """Parse county and city references"""
        # County parsing with high confidence
        for county in self.GEORGIA_COUNTIES:
            patterns = [
                rf'\b{re.escape(county)}\s+county\b',
                rf'\bin\s+{re.escape(county)}\b',
                rf'\b{re.escape(county)}\s+ga\b'
            ]
            
            for pattern in patterns:
                if re.search(pattern, query):
                    self.filters.append(QueryFilter(
                        FilterType.COUNTY,
                        'ILIKE',
                        f'%{county}%'
                    ))
                    return  # Only match first county found

    def _parse_property_type(self, query: str):
        """Parse property types with synonym expansion"""
        found_types = []
        
        for canonical_type, synonyms in self.PROPERTY_SYNONYMS.items():
            # Skip status-related terms (handled separately)
            if canonical_type in ['vacant', 'for sale', 'sold']:
                continue
                
            for synonym in synonyms:
                if re.search(rf'\b{re.escape(synonym)}\b', query):
                    found_types.extend(synonyms)
                    break
        
        if found_types:
            # Remove duplicates and create filter
            unique_types = list(set(found_types))
            self.filters.append(QueryFilter(
                FilterType.PROPERTY_TYPE,
                'ILIKE_OR',
                unique_types
            ))

    def _parse_status(self, query: str):
        """Parse status with schema-aware mapping"""
        status_mappings = {
            'vacant': 'Vacant',
            'empty': 'Vacant', 
            'available': 'Available',
            'for sale': 'For Sale',
            'sold': 'Sold',
            'active': 'Active'
        }
        
        for term, db_status in status_mappings.items():
            if re.search(rf'\b{re.escape(term)}\b', query):
                self.filters.append(QueryFilter(
                    FilterType.STATUS,
                    '=',
                    db_status
                ))
                
                # For vacant, also check property_type as fallback
                if term == 'vacant':
                    self.filters.append(QueryFilter(
                        FilterType.PROPERTY_TYPE,
                        'ILIKE_FALLBACK',
                        'vacant'
                    ))
                break

    def _parse_size(self, query: str):
        """Parse size requirements with proper range handling"""
        # Acres parsing
        acres_range = re.search(self.SIZE_PATTERNS['acres'], query)
        if acres_range:
            min_acres, max_acres = acres_range.groups()
            self.filters.append(QueryFilter(
                FilterType.SIZE_ACRES,
                'BETWEEN',
                float(min_acres),
                float(max_acres)
            ))
            self.columns.append('size_acres')
            return
        
        acres_single = re.search(self.SIZE_PATTERNS['acres_single'], query)
        if acres_single:
            acres_value = float(acres_single.group(1))
            # Check context for comparison
            if re.search(r'over\s+' + re.escape(acres_single.group(0)), query):
                self.filters.append(QueryFilter(FilterType.SIZE_ACRES, '>=', acres_value))
            elif re.search(r'under\s+' + re.escape(acres_single.group(0)), query):
                self.filters.append(QueryFilter(FilterType.SIZE_ACRES, '<=', acres_value))
            else:
                self.filters.append(QueryFilter(FilterType.SIZE_ACRES, '=', acres_value))
            self.columns.append('size_acres')
            return
        
        # Square footage parsing
        sqft_range = re.search(self.SIZE_PATTERNS['sqft_range'], query)
        if sqft_range:
            min_sqft = int(sqft_range.group(1).replace(',', ''))
            max_sqft = int(sqft_range.group(2).replace(',', ''))
            
            # Determine if building or lot size based on context
            if re.search(r'building|structure|indoor', query):
                filter_type = FilterType.BUILDING_SQFT
                self.columns.append('building_sqft')
            else:
                filter_type = FilterType.SIZE_SQFT
                self.columns.append('size_sqft')
                
            self.filters.append(QueryFilter(
                filter_type,
                'BETWEEN',
                min_sqft,
                max_sqft
            ))
            return
        
        sqft_single = re.search(self.SIZE_PATTERNS['sqft'], query)
        if sqft_single:
            sqft_value = int(sqft_single.group(1).replace(',', ''))
            
            # Context-based filtering
            if re.search(r'building|structure|indoor', query):
                filter_type = FilterType.BUILDING_SQFT
                self.columns.append('building_sqft')
            else:
                filter_type = FilterType.SIZE_SQFT  
                self.columns.append('size_sqft')
            
            # Check for comparison context
            if re.search(r'over\s+' + re.escape(sqft_single.group(0)), query):
                self.filters.append(QueryFilter(filter_type, '>=', sqft_value))
            elif re.search(r'under\s+' + re.escape(sqft_single.group(0)), query):
                self.filters.append(QueryFilter(filter_type, '<=', sqft_value))
            else:
                self.filters.append(QueryFilter(filter_type, '>=', sqft_value))

    def _parse_price(self, query: str):
        """Parse price requirements with k/m notation support"""
        def normalize_price(price_str: str) -> int:
            """Convert price string to integer (handle k, m suffixes)"""
            price_str = price_str.replace(',', '')
            if price_str.endswith('k'):
                return int(float(price_str[:-1]) * 1000)
            elif price_str.endswith('m'):
                return int(float(price_str[:-1]) * 1000000)
            else:
                return int(price_str)
        
        # Range prices
        between_match = re.search(self.PRICE_PATTERNS['between'], query)
        if between_match:
            min_price = normalize_price(between_match.group(1))
            max_price = normalize_price(between_match.group(2))
            self.filters.append(QueryFilter(
                FilterType.PRICE,
                'BETWEEN',
                min_price,
                max_price
            ))
            return
        
        # Under price
        under_match = re.search(self.PRICE_PATTERNS['under'], query)
        if under_match:
            max_price = normalize_price(under_match.group(1))
            self.filters.append(QueryFilter(FilterType.PRICE, '<=', max_price))
            return
        
        # Over price  
        over_match = re.search(self.PRICE_PATTERNS['over'], query)
        if over_match:
            min_price = normalize_price(over_match.group(1))
            self.filters.append(QueryFilter(FilterType.PRICE, '>=', min_price))
            return

    def _parse_ordering(self, query: str):
        """Determine appropriate ordering"""
        if any(word in query for word in ['cheapest', 'lowest', 'budget', 'under']):
            self.order_by = ('asking_price', 'ASC')
        elif any(word in query for word in ['expensive', 'highest', 'premium']):
            self.order_by = ('asking_price', 'DESC')
        elif any(word in query for word in ['biggest', 'largest', 'most acres']):
            self.order_by = ('size_acres', 'DESC')
        elif any(word in query for word in ['smallest', 'least acres']):
            self.order_by = ('size_acres', 'ASC')
        elif 'mixed' in query and 'acres' in query:
            # For mixed results, order by asking price instead of size
            self.order_by = ('asking_price', 'ASC')
        elif any(word in query for word in ['2 to 5', '2-5', 'between 2 and 5']) and 'acres' in query:
            # For range queries, show variety by ordering by price
            self.order_by = ('asking_price', 'ASC')
        elif 'acres' in query:
            self.order_by = ('size_acres', 'ASC')  # Changed to ASC for better variety
        elif any(word in query for word in ['sqft', 'square']):
            self.order_by = ('size_sqft', 'DESC')
        else:
            self.order_by = ('asking_price', 'ASC')

    def _determine_columns(self):
        """Add relevant columns based on filters"""
        # Always include core columns
        base_columns = ['id', 'name', 'property_type', 'property_subtype', 'asking_price']
        
        for filter_item in self.filters:
            if filter_item.filter_type == FilterType.SIZE_ACRES and 'size_acres' not in self.columns:
                self.columns.append('size_acres')
            elif filter_item.filter_type == FilterType.SIZE_SQFT and 'size_sqft' not in self.columns:
                self.columns.append('size_sqft')
            elif filter_item.filter_type == FilterType.BUILDING_SQFT and 'building_sqft' not in self.columns:
                self.columns.append('building_sqft')
            elif filter_item.filter_type == FilterType.TRAFFIC and 'traffic_count_aadt' not in self.columns:
                self.columns.append('traffic_count_aadt')
        
        # Ensure base columns are first
        final_columns = []
        for col in base_columns:
            if col not in final_columns:
                final_columns.append(col)
        
        for col in self.columns:
            if col not in final_columns:
                final_columns.append(col)
                
        self.columns = final_columns

class SQLGenerator:
    """Convert parsed query to optimized SQL"""
    
    def __init__(self, table_name: str = "Georgia Properties"):
        self.table_name = table_name

    def generate(self, parsed_query: ParsedQuery) -> str:
        """Generate SQL from parsed query"""
        
        # Handle aggregation queries
        if parsed_query.is_aggregate:
            return self._generate_aggregate_sql(parsed_query)
        
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
    
    def _generate_aggregate_sql(self, parsed_query: ParsedQuery) -> str:
        """Generate SQL for aggregation queries"""
        
        if parsed_query.aggregate_type == 'county_count':
            return """SELECT address->>'county' AS county, COUNT(*) AS property_count
FROM "Georgia Properties"
WHERE address->>'county' IS NOT NULL
GROUP BY address->>'county'
ORDER BY property_count DESC"""
        
        elif parsed_query.aggregate_type == 'type_count':
            return """SELECT property_type, COUNT(*) AS property_count
FROM "Georgia Properties"
WHERE property_type IS NOT NULL
GROUP BY property_type
ORDER BY property_count DESC"""
        
        elif parsed_query.aggregate_type == 'total_count':
            return """SELECT COUNT(*) AS total_properties
FROM "Georgia Properties" """
        
        else:
            # Default aggregation
            return f"SELECT {', '.join(parsed_query.columns)} FROM \"{self.table_name}\""

    def _build_condition(self, filter_item: QueryFilter) -> str:
        """Build individual WHERE condition"""
        if filter_item.filter_type == FilterType.COUNTY:
            return f"address->>'county' ILIKE '{filter_item.value}'"
        
        elif filter_item.filter_type == FilterType.CITY:
            return f"address->>'city' ILIKE '{filter_item.value}'"
        
        elif filter_item.filter_type == FilterType.PROPERTY_TYPE:
            if filter_item.operator == 'ILIKE_OR':
                # Multiple synonyms
                conditions = []
                for synonym in filter_item.value:
                    conditions.extend([
                        f"property_type ILIKE '%{synonym}%'",
                        f"property_subtype ILIKE '%{synonym}%'"
                    ])
                return f"({' OR '.join(conditions)})"
            elif filter_item.operator == 'ILIKE_FALLBACK':
                # Fallback for vacant properties
                return f"(property_type ILIKE '%{filter_item.value}%' OR property_subtype ILIKE '%{filter_item.value}%')"
        
        elif filter_item.filter_type == FilterType.STATUS:
            return f"status = '{filter_item.value}'"
        
        elif filter_item.filter_type in [FilterType.SIZE_ACRES, FilterType.SIZE_SQFT, FilterType.BUILDING_SQFT, FilterType.PRICE, FilterType.TRAFFIC]:
            column_map = {
                FilterType.SIZE_ACRES: 'size_acres',
                FilterType.SIZE_SQFT: 'size_sqft', 
                FilterType.BUILDING_SQFT: 'building_sqft',
                FilterType.PRICE: 'asking_price',
                FilterType.TRAFFIC: 'traffic_count_aadt'
            }
            
            column = column_map[filter_item.filter_type]
            
            if filter_item.operator == 'BETWEEN':
                return f"{column} BETWEEN {filter_item.value} AND {filter_item.value2}"
            elif filter_item.operator in ['=', '>', '<', '>=', '<=']:
                return f"{column} {filter_item.operator} {filter_item.value}"
        
        return ""