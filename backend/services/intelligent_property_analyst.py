"""
Intelligent Property Analyst Chatbot
Acts like a real commercial real estate analyst specializing in gas stations and convenience stores
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import openai
from datetime import datetime
from .advanced_research_agent import AdvancedResearchAgent
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Maintains conversation context and memory"""
    property_address: str
    smarty_data: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    collected_data: Dict[str, Any]
    analysis_stage: str  # 'initial', 'gathering', 'analyzing', 'complete'
    confidence_level: float
    missing_data_points: List[str]
    user_preferences: Dict[str, Any]

@dataclass
class AnalystResponse:
    """Response from the intelligent analyst"""
    message: str
    follow_up_questions: List[str]
    data_collected: Dict[str, Any]
    analysis_stage: str
    confidence_level: float
    next_steps: List[str]
    requires_user_input: bool

class IntelligentPropertyAnalyst:
    """AI-powered property analyst that conducts intelligent conversations"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o"
        self.research_agent = AdvancedResearchAgent(openai_api_key)
        
        # Enhanced analyst personality with gas station feasibility focus
        self.system_prompt = """
        You are Rohit, a senior commercial real estate analyst with 15+ years of experience 
        specializing in gas station and convenience store FEASIBILITY analysis. You evaluate ANY property type 
        for potential gas station/convenience store development using advanced IMST methodology.

        MISSION: Determine if ANY property can be converted/developed into a profitable gas station/convenience store.

        Your personality:
        - Give SHORT, insightful responses (max 8 sentences)
        - Professional but analytical
        - Ask ONE strategic question at a time
        - Make intelligent assumptions when data is limited
        - Focus on gas station feasibility factors 

        CORE EXPERTISE (Speed Data LLC methodology):
        1. LOCATION ANALYSIS:
           - Traffic count analysis (critical for fuel sales)
           - Visibility from major roads and highways
           - Access quality and ingress/egress evaluation
           - Proximity to major arterials and interstates

        2. MARKET ANALYSIS:
           - Demographics (population density, income levels, age groups)
           - Market penetration potential for fuel retail
           - Economic conditions and growth projections
           - Target customer segments (commuters, locals, truckers)

        3. SITE EVALUATION:
           - Lot size adequacy for gas station layout (minimum 0.5 acres ideal)
           - Zoning compliance for fuel retail operations
           - Environmental and regulatory considerations
           - Infrastructure requirements (utilities, drainage)

        4. COMPETITION ANALYSIS:
           - Existing gas stations within 1-3 mile radius
           - Brand analysis (Chevron, Marathon, BP, Shell, etc.)
           - Service offerings (car wash, food service, convenience items)
           - Fuel pricing and competitive positioning

        Your approach:
        1. Acknowledge current property details
        2. Assess gas station development potential
        3. Gather critical feasibility data through targeted questions
        4. Provide intelligent projections even with limited data
        5. Build towards comprehensive feasibility recommendation
        5. Always explain your reasoning
        6. Remember user preferences and previous answers

        CRITICAL: Keep responses under 50 words. Be direct and focused. Ask ONE question at a time.
        """
        
        # Critical data points for gas station analysis
        self.critical_data_points = {
            'traffic_count': 'Daily traffic count (vehicles per day)',
            'visibility': 'Highway visibility and signage opportunities',
            'access': 'Ingress/egress quality and traffic light presence',
            'competition': 'Nearby gas stations within 1-mile radius',
            'demographics': 'Local population income and density',
            'zoning': 'Zoning compliance for gas station use',
            'corner_location': 'Corner vs mid-block positioning',
            'fuel_delivery': 'Fuel delivery truck accessibility',
            'brand_presence': 'Existing brand presence in market',
            'local_regulations': 'Local permitting and environmental requirements'
        }
        
        # Common location name corrections for Georgia
        self.location_corrections = {
            'jobesboro': 'jonesboro',
            'valdosta': 'valdosta',
            'savannah': 'savannah',
            'atlanta': 'atlanta',
            'macon': 'macon',
            'augusta': 'augusta',
            'columbus': 'columbus'
        }

    def normalize_address(self, address: str) -> str:
        """Standardize address format for consistent processing"""
        if not address:
            return ""
            
        # Convert to uppercase and strip whitespace
        normalized = address.upper().strip()
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Common abbreviation standardization
        abbreviations = {
            r'\bST\b': 'STREET',
            r'\bAVE\b': 'AVENUE', 
            r'\bAV\b': 'AVENUE',
            r'\bRD\b': 'ROAD',
            r'\bDR\b': 'DRIVE',
            r'\bBLVD\b': 'BOULEVARD',
            r'\bPKWY\b': 'PARKWAY',
            r'\bHWY\b': 'HIGHWAY',
            r'\bCT\b': 'COURT',
            r'\bPL\b': 'PLACE',
            r'\bLN\b': 'LANE',
            r'\bCIR\b': 'CIRCLE'
        }
        
        for abbrev, full in abbreviations.items():
            normalized = re.sub(abbrev, full, normalized)
        
        # Fix common location name variations using fuzzy matching
        words = normalized.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower()
            best_match = None
            best_ratio = 0
            
            for incorrect, correct in self.location_corrections.items():
                ratio = SequenceMatcher(None, word_lower, incorrect).ratio()
                if ratio > 0.8 and ratio > best_ratio:  # 80% similarity threshold
                    best_match = correct.upper()
                    best_ratio = ratio
            
            corrected_words.append(best_match if best_match else word)
        
        return ' '.join(corrected_words)

    def validate_address_consistency(self, current_address: str, context_address: str) -> bool:
        """Check if addresses refer to the same property"""
        normalized_current = self.normalize_address(current_address)
        normalized_context = self.normalize_address(context_address)
        
        # Extract key components for comparison
        def extract_key_components(addr):
            # Extract street number, street name, city
            parts = addr.split(',')
            if len(parts) >= 2:
                street_part = parts[0].strip()
                city_part = parts[1].strip() if len(parts) > 1 else ""
                return street_part, city_part
            return addr, ""
        
        current_street, current_city = extract_key_components(normalized_current)
        context_street, context_city = extract_key_components(normalized_context)
        
        # Check similarity
        street_similarity = SequenceMatcher(None, current_street, context_street).ratio()
        city_similarity = SequenceMatcher(None, current_city, context_city).ratio()
        
        return street_similarity > 0.9 and city_similarity > 0.8

    def validate_traffic_count(self, traffic_input: str, property_type: str = None, location_type: str = None) -> Tuple[bool, int, str]:
        """Validate and normalize traffic count input"""
        try:
            # Extract numeric value from input
            numbers = re.findall(r'\d+,?\d*', traffic_input.replace(',', ''))
            if not numbers:
                return False, 0, "No numeric traffic count found in input"
            
            traffic_count = int(numbers[0])
            
            # Define realistic ranges based on road types
            traffic_ranges = {
                'local_road': (500, 5000),
                'collector_road': (5000, 25000),
                'arterial_road': (15000, 50000),
                'highway': (25000, 100000),
                'interstate': (50000, 200000)
            }
            
            # Property type considerations
            property_traffic_caps = {
                'residential_vacant_land': 15000,
                'auto_repair_garage': 25000,
                'convenience_store': 75000,
                'gas_station': 100000,
                'condominium': 10000
            }
            
            # Apply property-specific cap if available
            max_realistic = property_traffic_caps.get(property_type, 50000)
            
            if traffic_count > max_realistic:
                return False, max_realistic, f"Traffic count {traffic_count:,} seems unrealistic for {property_type}. Maximum reasonable: {max_realistic:,}"
            
            if traffic_count < 100:
                return False, 1000, f"Traffic count {traffic_count} seems too low. Minimum reasonable: 1,000"
            
            return True, traffic_count, "Valid traffic count"
            
        except Exception as e:
            logger.error(f"Error validating traffic count: {e}")
            return False, 0, "Invalid traffic count format"

    def validate_demographics(self, demographic_input: str, county: str = None) -> Tuple[bool, Dict, str]:
        """Validate and normalize demographic input"""
        try:
            # Extract population numbers
            numbers = re.findall(r'\d+,?\d*', demographic_input.replace(',', ''))
            
            if not numbers:
                return False, {}, "No numeric demographic data found"
            
            population = int(numbers[0])
            
            # Georgia county population ranges for validation
            county_population_ranges = {
                'fulton': (500000, 1100000),
                'gwinnett': (800000, 1000000),
                'dekalb': (700000, 800000),
                'cobb': (700000, 800000),
                'chatham': (250000, 300000),
                'clayton': (250000, 300000),
                'richmond': (200000, 250000),
                'henry': (200000, 250000)
            }
            
            # Local area population should be much smaller than county
            max_local_population = 50000  # For immediate area around property
            
            if population > max_local_population:
                return False, {'population': max_local_population}, f"Local area population {population:,} seems too high. Maximum reasonable: {max_local_population:,}"
            
            if population < 500:
                return False, {'population': 2000}, f"Population {population} seems too low. Minimum reasonable: 2,000"
            
            # Try to extract income if mentioned
            income_keywords = ['income', 'salary', 'earning']
            income = None
            for keyword in income_keywords:
                if keyword in demographic_input.lower():
                    income_numbers = re.findall(r'\$?\d+,?\d*k?', demographic_input.lower())
                    if income_numbers:
                        income_str = income_numbers[0].replace('$', '').replace('k', '000').replace(',', '')
                        income = int(income_str)
                        break
            
            result = {'population': population}
            if income:
                if 20000 <= income <= 200000:  # Reasonable income range
                    result['median_income'] = income
                else:
                    result['median_income'] = 55000  # Georgia median
            
            return True, result, "Valid demographic data"
            
        except Exception as e:
            logger.error(f"Error validating demographics: {e}")
            return False, {}, "Invalid demographic format"

    def validate_competition_data(self, competition_input: str) -> Tuple[bool, int, str]:
        """Validate and normalize competition data"""
        try:
            # Extract numeric values
            numbers = re.findall(r'\d+', competition_input)
            
            if not numbers:
                # Try to extract from text descriptions
                competition_keywords = {
                    'none': 0, 'zero': 0, 'no': 0,
                    'one': 1, 'single': 1,
                    'two': 2, 'couple': 2,
                    'three': 3, 'few': 3,
                    'four': 4, 'five': 5,
                    'several': 6, 'many': 8
                }
                
                competition_input_lower = competition_input.lower()
                for keyword, count in competition_keywords.items():
                    if keyword in competition_input_lower:
                        return True, count, f"Interpreted '{keyword}' as {count} competitors"
                
                return False, 3, "Could not determine competition count from input"
            
            competition_count = int(numbers[0])
            
            # Reasonable competition ranges
            if competition_count > 20:
                return False, 10, f"Competition count {competition_count} seems unrealistic. Maximum reasonable: 10"
            
            if competition_count < 0:
                return False, 0, "Competition count cannot be negative"
            
            return True, competition_count, "Valid competition data"
            
        except Exception as e:
            logger.error(f"Error validating competition: {e}")
            return False, 3, "Invalid competition format"

    def calculate_imst_score(self, context: ConversationContext) -> Tuple[float, Dict[str, float], str]:
        """Calculate consistent IMST score with validated inputs"""
        try:
            # Extract and validate data
            traffic_data = context.collected_data.get('traffic_count', '')
            competition_data = context.collected_data.get('competition', '')
            demographics_data = context.collected_data.get('demographics', '')
            
            property_info = context.smarty_data.get('property_info', {})
            property_type = property_info.get('property_type', 'unknown')
            lot_acres = float(property_info.get('acres', 0.5))
            building_sqft = property_info.get('building_sqft', 'Unknown')
            
            # Initialize scores with reasonable defaults when data is missing
            scores = {
                'location': 5.0,  # Default moderate score
                'market': 5.0,    # Default moderate score
                'site': 0.0,      # Will be calculated from property data
                'competition': 5.0  # Default moderate score (assume average competition)
            }
            
            # LOCATION SCORE (Traffic + Visibility + Access)
            if traffic_data:
                valid_traffic, traffic_count, _ = self.validate_traffic_count(str(traffic_data), property_type)
                if valid_traffic:
                    # Traffic scoring based on ranges
                    if traffic_count >= 30000:
                        traffic_score = 10
                    elif traffic_count >= 20000:
                        traffic_score = 8
                    elif traffic_count >= 15000:
                        traffic_score = 7
                    elif traffic_count >= 10000:
                        traffic_score = 6
                    elif traffic_count >= 5000:
                        traffic_score = 4
                    else:
                        traffic_score = 2
                    
                    # Adjust for property type suitability
                    if property_type in ['gas_station', 'convenience_store']:
                        traffic_score = min(10, traffic_score + 1)
                    elif property_type in ['residential_vacant_land', 'condominium']:
                        traffic_score = max(1, traffic_score - 1)
                    
                    scores['location'] = traffic_score
            
            # MARKET SCORE (Demographics + Economic Factors)
            if demographics_data:
                valid_demo, demo_dict, _ = self.validate_demographics(str(demographics_data))
                if valid_demo:
                    population = demo_dict.get('population', 5000)
                    income = demo_dict.get('median_income', 50000)
                    
                    # Population density scoring
                    if population >= 25000:
                        pop_score = 10
                    elif population >= 15000:
                        pop_score = 8
                    elif population >= 10000:
                        pop_score = 6
                    elif population >= 5000:
                        pop_score = 4
                    else:
                        pop_score = 2
                    
                    # Income level scoring
                    if income >= 75000:
                        income_score = 10
                    elif income >= 60000:
                        income_score = 8
                    elif income >= 50000:
                        income_score = 6
                    elif income >= 40000:
                        income_score = 4
                    else:
                        income_score = 2
                    
                    scores['market'] = (pop_score + income_score) / 2
            
            # SITE SCORE (Lot Size + Zoning + Development Potential) - ALWAYS CALCULATED
            # Lot size scoring for gas station development
            if lot_acres >= 1.0:
                lot_score = 10
            elif lot_acres >= 0.75:
                lot_score = 8
            elif lot_acres >= 0.5:
                lot_score = 6
            elif lot_acres >= 0.25:
                lot_score = 4
            else:
                lot_score = 2
            
            # Building condition/age factor
            year_built = property_info.get('year_built', 'Unknown')
            building_score = 5  # Default
            
            if year_built != 'Unknown' and str(year_built).isdigit():
                year = int(year_built)
                current_year = datetime.now().year
                age = current_year - year
                
                if age <= 10:
                    building_score = 9
                elif age <= 20:
                    building_score = 7
                elif age <= 30:
                    building_score = 5
                else:
                    building_score = 3
            
            # Property type bonus/penalty for gas station conversion
            if property_type in ['gas_station', 'convenience_store']:
                type_bonus = 1.5
            elif property_type in ['auto_repair_garage', 'retail']:
                type_bonus = 1.0
            elif property_type in ['residential_vacant_land']:
                type_bonus = 0.8  # More development needed
            else:
                type_bonus = 0.9
            
            scores['site'] = min(10, (lot_score + building_score) / 2 * type_bonus)
            
            # COMPETITION SCORE (Market Saturation)
            if competition_data:
                valid_comp, comp_count, _ = self.validate_competition_data(str(competition_data))
                if valid_comp:
                    # Lower competition = higher score
                    if comp_count == 0:
                        comp_score = 10
                    elif comp_count <= 2:
                        comp_score = 8
                    elif comp_count <= 4:
                        comp_score = 6
                    elif comp_count <= 6:
                        comp_score = 4
                    else:
                        comp_score = 2
                    
                    scores['competition'] = comp_score
            
            # Calculate weighted overall score with property-specific adjustments
            weights = {
                'location': 0.35,  # Traffic is critical for gas stations
                'market': 0.25,   # Demographics important
                'site': 0.25,     # Site suitability
                'competition': 0.15  # Competition factor
            }
            
            overall_score = sum(scores[category] * weights[category] for category in scores)
            
            # Add property-specific variations to prevent identical scores
            financial_info = context.smarty_data.get('financial_info', {})
            market_value = financial_info.get('market_value', '$0')
            value_number = int(re.findall(r'\d+', market_value.replace(',', ''))[0]) if re.findall(r'\d+', market_value.replace(',', '')) else 0
            
            # Value-based adjustment (small variation)
            if value_number > 1000000:  # High value property
                overall_score += 0.3
            elif value_number > 500000:  # Medium value
                overall_score += 0.1
            elif value_number < 50000:  # Low value
                overall_score -= 0.2
            
            # Location-based variation (county/city factors)
            county = context.smarty_data.get('county', '').lower()
            city = context.smarty_data.get('city', '').lower()
            
            # Georgia economic factors
            if county in ['fulton', 'gwinnett', 'cobb', 'dekalb']:  # Atlanta metro
                overall_score += 0.4
            elif county in ['chatham']:  # Savannah
                overall_score += 0.2
            elif county in ['richmond']:  # Augusta
                overall_score += 0.1
            elif county in ['grady', 'thomas']:  # Rural counties
                overall_score -= 0.3
            
            # Property type final adjustment
            if property_type == 'gas_station':
                overall_score += 0.5  # Already optimized
            elif property_type == 'convenience_store':
                overall_score += 0.3
            elif property_type == 'auto_repair_garage':
                overall_score += 0.1
            elif property_type == 'residential_vacant_land':
                overall_score -= 0.2  # Needs more development
            elif property_type == 'condominium':
                overall_score -= 0.5  # Poor fit for gas station
            
            # Generate recommendation based on score
            if overall_score >= 8.0:
                recommendation = "STRONG BUY"
            elif overall_score >= 7.0:
                recommendation = "BUY"
            elif overall_score >= 5.0:
                recommendation = "INVESTIGATE"
            else:
                recommendation = "PASS"
            
            return round(overall_score, 1), scores, recommendation
            
        except Exception as e:
            logger.error(f"Error calculating IMST score: {e}")
            return 5.0, {'location': 5, 'market': 5, 'site': 5, 'competition': 5}, "INVESTIGATE"

    def _validate_and_normalize_collected_data(self, context: ConversationContext) -> None:
        """Validate and normalize all collected data in the context"""
        property_type = context.smarty_data.get('property_info', {}).get('property_type', 'unknown')
        
        # Validate traffic data
        if 'traffic_count' in context.collected_data:
            traffic_input = str(context.collected_data['traffic_count'])
            valid, normalized_traffic, message = self.validate_traffic_count(traffic_input, property_type)
            
            if not valid:
                logger.warning(f"Traffic validation failed: {message}")
                context.collected_data['traffic_count'] = f"{normalized_traffic:,} vehicles/day (adjusted from unrealistic input)"
                context.collected_data['traffic_validation_message'] = message
            else:
                context.collected_data['traffic_count'] = f"{normalized_traffic:,} vehicles/day"
        
        # Validate demographics
        if 'demographics' in context.collected_data:
            demo_input = str(context.collected_data['demographics'])
            valid, normalized_demo, message = self.validate_demographics(demo_input)
            
            if not valid:
                logger.warning(f"Demographics validation failed: {message}")
                context.collected_data['demographics_validation_message'] = message
            
            if normalized_demo:
                demo_text = f"Population: {normalized_demo.get('population', 'Unknown'):,}"
                if 'median_income' in normalized_demo:
                    demo_text += f", Median Income: ${normalized_demo['median_income']:,}"
                context.collected_data['demographics'] = demo_text
        
        # Validate competition
        if 'competition' in context.collected_data:
            comp_input = str(context.collected_data['competition'])
            valid, normalized_comp, message = self.validate_competition_data(comp_input)
            
            if not valid:
                logger.warning(f"Competition validation failed: {message}")
                context.collected_data['competition_validation_message'] = message
            
            context.collected_data['competition'] = f"{normalized_comp} gas stations within 1-3 miles"

    def _format_final_score(self, overall_score: float, category_scores: Dict[str, float], recommendation: str, context: ConversationContext) -> str:
        """Generate consistently formatted final score response"""
        property_info = context.smarty_data.get('property_info', {})
        financial_info = context.smarty_data.get('financial_info', {})
        
        current_type = property_info.get('property_type', 'Unknown').replace('_', ' ').title()
        lot_size = property_info.get('acres', 'Unknown')
        building_size = property_info.get('building_sqft', 'Unknown')
        market_value = financial_info.get('market_value', 'Unknown')
        
        # Generate financial projections based on scores
        monthly_fuel_volume = self._estimate_fuel_volume(overall_score, context.collected_data)
        monthly_cstore_sales = self._estimate_cstore_sales(overall_score, context.collected_data)
        total_monthly_revenue = monthly_fuel_volume * 0.15 + monthly_cstore_sales  # Rough fuel margin + c-store
        
        # Create a wide, clean formatted response
        traffic_display = context.collected_data.get('traffic_count', 'Not provided')
        demographics_display = context.collected_data.get('demographics', 'Analysis needed')
        competition_display = context.collected_data.get('competition', 'Assessment needed')
        
        response = f"""

🏢 GAS STATION FEASIBILITY ANALYSIS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

📍 PROPERTY OVERVIEW
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
• Current Use: {current_type}                    • Lot Size: {lot_size} acres                    • Building: {building_size} sq ft
• Market Value: {market_value}                   • Conversion Potential: {"Excellent" if overall_score >= 7 else "Good" if overall_score >= 5 else "Limited"}


📊 IMST SCORING BREAKDOWN
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

🚗 LOCATION SCORE: {category_scores.get('location', 0):.1f}/10
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Traffic Count: {traffic_display}                    Visibility: {"High" if category_scores.get('location', 0) >= 7 else "Moderate" if category_scores.get('location', 0) >= 5 else "Limited"}                    Access: {"Excellent" if category_scores.get('location', 0) >= 8 else "Good" if category_scores.get('location', 0) >= 6 else "Standard"}


👥 MARKET SCORE: {category_scores.get('market', 0):.1f}/10
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Demographics: {demographics_display}                    Opportunity: {"Strong" if category_scores.get('market', 0) >= 7 else "Moderate" if category_scores.get('market', 0) >= 5 else "Limited"}


🏗️ SITE SCORE: {category_scores.get('site', 0):.1f}/10
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Lot Adequacy: {self._get_lot_adequacy_description(lot_size)}                    Development Cost: {"Low" if category_scores.get('site', 0) >= 7 else "Moderate" if category_scores.get('site', 0) >= 5 else "High"}


⛽ COMPETITION SCORE: {category_scores.get('competition', 0):.1f}/10
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Market Saturation: {competition_display}                    Position: {"Dominant" if category_scores.get('competition', 0) >= 9 else "Strong" if category_scores.get('competition', 0) >= 7 else "Competitive"}


💰 FINANCIAL PROJECTIONS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Monthly Fuel Volume: {monthly_fuel_volume:,.0f} gallons          Monthly C-Store Sales: ${monthly_cstore_sales:,.0f}          Total Revenue: ${total_monthly_revenue:,.0f}


🎯 OVERALL FEASIBILITY SCORE: {overall_score}/10          📈 RECOMMENDATION: {recommendation}


✅ KEY STRENGTHS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
• {self._get_success_factors(overall_score, category_scores)[0]}
• {self._get_success_factors(overall_score, category_scores)[1]}


⚠️ RISK FACTORS
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
• {self._get_risk_factors(overall_score, category_scores)[0]}
• {self._get_risk_factors(overall_score, category_scores)[1]}


💡 Speed Data LLC Methodology Applied
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

"""
        
        return response

    def _estimate_fuel_volume(self, score: float, collected_data: Dict) -> float:
        """Estimate monthly fuel volume based on score and data"""
        base_volume = 50000  # Base monthly gallons
        
        # Adjust based on traffic
        traffic_str = collected_data.get('traffic_count', '10000')
        traffic_numbers = re.findall(r'\d+', traffic_str.replace(',', ''))
        if traffic_numbers:
            daily_traffic = int(traffic_numbers[0])
            # Assume 2-5% of traffic stops for fuel
            fuel_customers_per_day = daily_traffic * 0.03
            monthly_volume = fuel_customers_per_day * 12 * 30  # 12 gallons average per customer
            return min(monthly_volume, 200000)  # Cap at realistic maximum
        
        return base_volume * (score / 10)

    def _estimate_cstore_sales(self, score: float, collected_data: Dict) -> float:
        """Estimate monthly convenience store sales"""
        base_sales = 80000  # Base monthly sales
        
        # Adjust based on demographics and traffic
        return base_sales * (score / 10) * 1.5  # C-store sales typically higher margin

    def _get_success_factors(self, score: float, category_scores: Dict) -> List[str]:
        """Generate success factors based on scores"""
        factors = []
        
        if category_scores.get('location', 0) >= 7:
            factors.append("Strong traffic flow supports fuel sales")
        elif category_scores.get('location', 0) >= 5:
            factors.append("Adequate traffic for viable operation")
        else:
            factors.append("Location requires traffic improvement analysis")
            
        if category_scores.get('competition', 0) >= 7:
            factors.append("Low competition provides market opportunity")
        elif category_scores.get('competition', 0) >= 5:
            factors.append("Moderate competition allows market entry")
        else:
            factors.append("Competitive differentiation strategy needed")
            
        if category_scores.get('site', 0) >= 7:
            factors.append("Site well-suited for gas station development")
        elif category_scores.get('site', 0) >= 5:
            factors.append("Site development feasible with planning")
        else:
            factors.append("Site challenges require engineering solutions")
            
        return factors[:3]

    def _get_risk_factors(self, score: float, category_scores: Dict) -> List[str]:
        """Generate risk factors based on scores"""
        risks = []
        
        if category_scores.get('location', 0) < 5:
            risks.append("Traffic volume may not support profitable operation")
        
        if category_scores.get('competition', 0) < 5:
            risks.append("High competition could limit market share")
            
        if category_scores.get('site', 0) < 5:
            risks.append("Site development costs may be prohibitive")
            
        if category_scores.get('market', 0) < 5:
            risks.append("Demographics may not support premium fuel sales")
            
        # Add generic risks if specific ones aren't triggered
        if len(risks) < 3:
            generic_risks = [
                "Regulatory approval required for fuel retail",
                "Environmental compliance costs",
                "Capital investment requirements significant"
            ]
            risks.extend(generic_risks[:3-len(risks)])
            
        return risks[:3]

    def _get_lot_adequacy_description(self, lot_size) -> str:
        """Get lot adequacy description based on size"""
        try:
            if str(lot_size).replace('.', '').replace('-', '').isdigit():
                size_float = float(lot_size)
                if size_float >= 1.0:
                    return "Excellent for gas station layout"
                elif size_float >= 0.5:
                    return "Adequate for gas station development"
                else:
                    return "Limited - may require adjacent land acquisition"
            else:
                return "Size assessment required"
        except (ValueError, TypeError):
            return "Size assessment required"

    async def start_analysis(self, property_address: str, smarty_data: Dict) -> AnalystResponse:
        """Start the property analysis conversation"""
        
        # Normalize address for consistency
        normalized_address = self.normalize_address(property_address)
        logger.info(f"Normalized address: '{property_address}' → '{normalized_address}'")
        
        # Create initial context
        context = ConversationContext(
            property_address=normalized_address,
            smarty_data=smarty_data,
            conversation_history=[],
            collected_data={},
            analysis_stage='initial',
            confidence_level=0.3,
            missing_data_points=list(self.critical_data_points.keys()),
            user_preferences={}
        )
        
        # Generate opening message
        # Debug: Log the smarty data being passed
        logger.info(f"Smarty data being analyzed: {smarty_data}")
        
        opening_prompt = f"""
        You are Rohit, a gas station feasibility analyst. Analyze this property for GAS STATION/CONVENIENCE STORE development potential:

        PROPERTY DATA FROM SMARTY API:
        {self._format_smarty_data(smarty_data)}

        FORMAT YOUR GREETING WITH WIDE LAYOUT:

        🏢 GAS STATION FEASIBILITY ANALYSIS
        ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
        
        📍 ANALYZING: [mention property details: sq ft, value, type]
        
        🚗 NEED: Daily traffic count for this location?
        
        ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

        Keep it short and wide.
        """

        try:
            property_info = smarty_data.get('property_info', {})
            property_context = f"CURRENT PROPERTY: {property_address} - {property_info.get('property_type', 'Unknown')} - {property_info.get('acres', 'Unknown')} acres"
            response = await self._call_llm(opening_prompt, [], property_context)
            
            # Parse the response to extract follow-up questions
            follow_up_questions = self._extract_questions(response)
            
            return AnalystResponse(
                message=response,
                follow_up_questions=follow_up_questions,
                data_collected={},
                analysis_stage='initial',
                confidence_level=0.3,
                next_steps=['Gather traffic data', 'Assess competition', 'Evaluate demographics'],
                requires_user_input=True
            )
            
        except Exception as e:
            logger.error(f"Error starting analysis: {e}")
            return AnalystResponse(
                message="I'm sorry, I'm having technical difficulties. Let me try again in a moment.",
                follow_up_questions=[],
                data_collected={},
                analysis_stage='error',
                confidence_level=0.0,
                next_steps=[],
                requires_user_input=False
            )

    async def continue_conversation(self, context: ConversationContext, user_message: str) -> AnalystResponse:
        """Continue the analysis conversation based on user input"""
        
        # Add user message to history
        context.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Validate and analyze user input with data validation
        context = await self._update_context_from_input(context, user_message)
        
        # Apply data validation to collected data
        self._validate_and_normalize_collected_data(context)
        
        # Generate intelligent response
        missing_critical = [dp for dp in context.missing_data_points if dp in ['traffic_count', 'competition', 'demographics']][:1]
        
        # Check if user wants to continue with limited data
        if "continue with available data" in user_message.lower() or "limited data" in user_message.lower():
            context.analysis_stage = 'complete'
            context.confidence_level = 0.7  # Lower confidence but complete
        
        # Check if we have enough data to complete analysis
        critical_data_collected = len([k for k in ['traffic_count', 'competition', 'demographics'] if k in context.collected_data])
        if critical_data_collected >= 2:  # If we have at least 2 critical data points
            context.analysis_stage = 'complete'
            context.confidence_level = max(0.7, context.confidence_level)
        
        # Check if user wants research mode
        if "research" in user_message.lower() or "find missing data" in user_message.lower():
            logger.info("User requested research mode - starting advanced research")
            research_results = await self.research_agent.research_missing_data(
                context.property_address, 
                context.smarty_data, 
                context.missing_data_points
            )
            
            # Add researched data to context
            context.collected_data.update(research_results)
            
            # Update missing data points
            for key in research_results.keys():
                if key in context.missing_data_points:
                    context.missing_data_points.remove(key)
            
            context.confidence_level = min(1.0, context.confidence_level + 0.3)
            context.analysis_stage = 'analyzing'
        
        # Check if user is asking for final analysis
        final_triggers = ["final score", "run final", "final analysis", "complete analysis", "imst score", "scoring"]
        should_complete = any(trigger in user_message.lower() for trigger in final_triggers)
        
        # Only complete if explicitly requested or we have enough data
        if should_complete or (len(context.collected_data) >= 3 and context.analysis_stage != 'complete'):
            context.analysis_stage = 'complete'
            # Generate final score immediately
            final_score_message = await self.generate_final_score(context)
            
            # Store conversation for learning
            try:
                from conversation_storage import conversation_storage
                overall_score, _, _ = self.calculate_imst_score(context)
                conversation_storage.store_conversation(
                    session_id=f"session_{hash(str(context.property_address))}",
                    property_address=context.property_address,
                    conversation_history=context.conversation_history,
                    final_score=overall_score
                )
            except Exception as e:
                logger.warning(f"Could not store conversation: {e}")
                
            return AnalystResponse(
                message=final_score_message,
                follow_up_questions=[],
                data_collected=context.collected_data,
                analysis_stage='complete',
                confidence_level=1.0,
                next_steps=[],
                requires_user_input=False
            )
        
        # Continue normal conversation
        conversation_prompt = f"""
        You are Rohit, a gas station feasibility analyst. 
        
        CURRENT PROPERTY:
        {self._format_smarty_data(context.smarty_data)}
        
        USER PROVIDED DATA SO FAR:
        {json.dumps(context.collected_data, indent=2)}
        
        USER JUST SAID: "{user_message}"
        
        RESPOND CLEANLY:
        - "what data u have" → List property details in bullet points
        - "who are u" → "I'm Rohit, gas station feasibility analyst"
        - New data provided → "Got it. [Next question]?"
        - "run scores/final" → Trigger full analysis
        
        Keep responses SHORT (under 30 words) and well-formatted.
        """

        try:
            property_info = context.smarty_data.get('property_info', {})
            property_context = f"CURRENT PROPERTY ONLY: {context.property_address} - {property_info.get('property_type', 'Unknown')} - {property_info.get('acres', 'Unknown')} acres - Market Value: {context.smarty_data.get('financial_info', {}).get('market_value', 'Unknown')}"
            response = await self._call_llm(conversation_prompt, context.conversation_history, property_context)
            
            # Update context based on response
            context.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Determine next steps
            next_steps = await self._determine_next_steps(context)
            
            return AnalystResponse(
                message=response,
                follow_up_questions=self._extract_questions(response),
                data_collected=context.collected_data,
                analysis_stage=context.analysis_stage,
                confidence_level=context.confidence_level,
                next_steps=next_steps,
                requires_user_input=context.confidence_level < 0.8
            )
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return AnalystResponse(
                message="I apologize, I'm having trouble processing that. Could you repeat that in different words?",
                follow_up_questions=[],
                data_collected=context.collected_data,
                analysis_stage=context.analysis_stage,
                confidence_level=context.confidence_level,
                next_steps=[],
                requires_user_input=True
            )

    async def _update_context_from_input(self, context: ConversationContext, user_input: str) -> ConversationContext:
        """Extract and update context from user input - simplified approach"""
        
        # Simple keyword-based extraction instead of JSON parsing
        user_lower = user_input.lower()
        
        # Check for traffic data
        if any(word in user_lower for word in ['traffic', 'vehicles', 'cars', 'vpd', 'daily']):
            # Extract numbers from user input
            import re
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                traffic_count = max([int(n) for n in numbers if int(n) > 100])  # Reasonable traffic count
                context.collected_data['traffic_count'] = f"{traffic_count} vehicles/day"
                if 'traffic_count' in context.missing_data_points:
                    context.missing_data_points.remove('traffic_count')
                context.confidence_level = min(1.0, context.confidence_level + 0.2)
        
        # Check for competition data
        if any(word in user_lower for word in ['gas station', 'competitor', 'competition', 'nearby', 'stations']):
            context.collected_data['competition'] = user_input
            if 'competition' in context.missing_data_points:
                context.missing_data_points.remove('competition')
            context.confidence_level = min(1.0, context.confidence_level + 0.2)
        
        # Check for demographics
        if any(word in user_lower for word in ['income', 'population', 'demographic', 'residents', 'people']):
            context.collected_data['demographics'] = user_input
            if 'demographics' in context.missing_data_points:
                context.missing_data_points.remove('demographics')
            context.confidence_level = min(1.0, context.confidence_level + 0.2)
        
        # Check for visibility/access
        if any(word in user_lower for word in ['visible', 'visibility', 'highway', 'access', 'entrance']):
            context.collected_data['visibility'] = user_input
            if 'visibility' in context.missing_data_points:
                context.missing_data_points.remove('visibility')
            context.confidence_level = min(1.0, context.confidence_level + 0.1)
        
        # Update analysis stage based on confidence
        if context.confidence_level >= 0.8:
            context.analysis_stage = 'complete'
        elif context.confidence_level >= 0.6:
            context.analysis_stage = 'analyzing'
        else:
            context.analysis_stage = 'gathering'
        
        return context

    async def generate_final_score(self, context: ConversationContext) -> str:
        """Generate dynamic IMST feasibility score using Speed Data LLC methodology"""
        
        property_info = context.smarty_data.get('property_info', {})
        financial_info = context.smarty_data.get('financial_info', {})
        current_property_type = property_info.get('property_type', 'unknown property')
        
        scoring_prompt = f"""
        You are analyzing the feasibility of converting/developing this {current_property_type} into a GAS STATION/CONVENIENCE STORE.

        CURRENT PROPERTY:
        - Address: {context.property_address}
        - Current Type: {current_property_type}
        - Lot Size: {property_info.get('lot_sqft', 'Unknown')} sq ft ({property_info.get('acres', 'Unknown')} acres)
        - Building: {property_info.get('building_sqft', 'Unknown')} sq ft
        - Year Built: {property_info.get('year_built', 'Unknown')}
        - Zoning: {property_info.get('zoning', 'Unknown')}
        - Market Value: {financial_info.get('market_value', 'Unknown')}

        USER PROVIDED DATA:
        {json.dumps(context.collected_data, indent=2)}

        Using Speed Data LLC methodology, analyze GAS STATION FEASIBILITY:

        1. LOCATION SCORE (0-10):
        - Traffic Count: Analyze fuel sales potential based on vehicle count
        - Visibility: Highway/arterial road visibility for brand recognition
        - Access: Ingress/egress quality for fuel customers
        
        2. MARKET SCORE (0-10):
        - Demographics: Population density, income levels, commuter patterns
        - Market Gap: Unserved fuel demand in the area
        - Growth Potential: Economic development trends
        
        3. SITE SCORE (0-10):
        - Lot Adequacy: Minimum 0.5 acres needed for gas station layout
        - Zoning: Fuel retail compatibility
        - Development Cost: Conversion/construction feasibility
        
        4. COMPETITION SCORE (0-10):
        - Market Saturation: Existing gas stations within 1-3 miles
        - Competitive Advantage: Potential differentiation opportunities
        - Market Share Potential: Revenue capture possibility

        FORMAT YOUR RESPONSE WITH CLEAN UI ELEMENTS:

        🏢 **GAS STATION FEASIBILITY ANALYSIS**
        
        📍 **PROPERTY OVERVIEW:**
        • Current Use: [current property type]
        • Conversion Potential: [assessment]
        
        📊 **IMST ANALYSIS:**
        
        **🚗 LOCATION SCORE: X/10**
        • Traffic: [analysis]
        • Visibility: [assessment]
        • Access: [evaluation]
        
        **👥 MARKET SCORE: X/10** 
        • Demographics: [analysis]
        • Market Gap: [opportunity assessment]
        • Growth: [potential]
        
        **🏗️ SITE SCORE: X/10**
        • Lot Size: [adequacy for gas station]
        • Zoning: [compliance assessment]
        • Development: [cost/feasibility]
        
        **⛽ COMPETITION SCORE: X/10**
        • Market Saturation: [analysis]
        • Competitive Position: [assessment]
        • Market Share: [potential]
        
        💰 **FINANCIAL PROJECTIONS:**
        • Monthly Fuel Volume: XXX,XXX gallons
        • Monthly C-Store Sales: $XXX,XXX
        • Total Monthly Revenue: $XXX,XXX
        
        🎯 **OVERALL FEASIBILITY: X.X/10**
        
        📈 **RECOMMENDATION: [STRONG BUY/BUY/INVESTIGATE/PASS]**
        
        ✅ **SUCCESS FACTORS:**
        • [Factor 1]
        • [Factor 2]
        • [Factor 3]
        
        ⚠️ **RISK FACTORS:**
        • [Risk 1]
        • [Risk 2]
        • [Risk 3]
        
        Use this exact format with emojis, headings, and bullet points. Make it visually appealing and easy to scan.
        """
        
        try:
            # Use the new consistent scoring algorithm
            overall_score, category_scores, recommendation = self.calculate_imst_score(context)
            
            # Generate formatted response using the calculated scores
            formatted_response = self._format_final_score(overall_score, category_scores, recommendation, context)
            return formatted_response
        except Exception as e:
            logger.error(f"Error generating feasibility score: {e}")
            # Intelligent fallback with basic analysis
            traffic = context.collected_data.get('traffic_count', 'Unknown')
            demographics = context.collected_data.get('demographics', 'Unknown')
            lot_size = property_info.get('acres', 'Unknown')
            
            return f"""
🏢 **GAS STATION FEASIBILITY ANALYSIS**

📍 **PROPERTY OVERVIEW:**
• Current Use: {current_property_type}
• Lot Size: {lot_size} acres
• Conversion Potential: Under evaluation

📊 **PRELIMINARY ASSESSMENT:**

**🚗 LOCATION ANALYSIS:**
• Traffic Count: {traffic}
• Visibility: Assessment needed
• Access: Evaluation required

**👥 MARKET ANALYSIS:**
• Demographics: {demographics}
• Market Gap: Analysis in progress
• Growth Potential: To be determined

**🏗️ SITE EVALUATION:**
• Lot Adequacy: {lot_size} acres available
• Zoning: Compliance check needed
• Development Cost: Assessment required

**⛽ COMPETITION ANALYSIS:**
• Market Research: In progress
• Competitive Position: To be evaluated
• Market Share: Potential assessment needed

🎯 **PRELIMINARY FEASIBILITY: 6.5/10**

📈 **RECOMMENDATION: INVESTIGATE**

⚠️ **NEXT STEPS NEEDED:**
• Complete traffic count analysis
• Conduct competitive market research  
• Evaluate zoning and development requirements
• Assess financial projections and ROI potential

💡 **NOTE:** Full feasibility analysis requires additional data collection for accurate projections.
            """

    async def _determine_next_steps(self, context: ConversationContext) -> List[str]:
        """Determine what the analyst should do next"""
        
        if context.confidence_level >= 0.8:
            return ['Provide comprehensive IMST analysis', 'Generate investment recommendation']
        elif context.confidence_level >= 0.6:
            return ['Gather remaining critical data', 'Begin preliminary analysis']
        else:
            # Focus on most critical missing data
            priority_data = ['traffic_count', 'competition', 'demographics', 'visibility']
            missing_priority = [d for d in priority_data if d in context.missing_data_points]
            return [f'Ask about {self.critical_data_points[d]}' for d in missing_priority[:2]]

    def _format_smarty_data(self, smarty_data: Dict) -> str:
        """Format complete Smarty data for LLM consumption"""
        if not smarty_data:
            return "No property records available."
        
        # Extract all available data sections
        property_info = smarty_data.get('property_info', {})
        financial_info = smarty_data.get('financial_info', {})
        location_info = smarty_data.get('location_info', {})
        
        formatted = f"""
PROPERTY DETAILS:
- Type: {property_info.get('property_type', 'Unknown')}
- Building: {property_info.get('building_sqft', 'Unknown')} sq ft
- Lot: {property_info.get('lot_sqft', 'Unknown')} sq ft ({property_info.get('acres', 'Unknown')} acres)
- Zoning: {property_info.get('zoning', 'Unknown')}
- Year Built: {property_info.get('year_built', 'Unknown')}
- Owner: {property_info.get('owner_name', 'Unknown')} ({property_info.get('ownership_type', 'Unknown')})

FINANCIAL DATA:
- Market Value: {financial_info.get('market_value', 'Unknown')}
- Last Sale: {financial_info.get('deed_sale_price', 'Unknown')} on {financial_info.get('deed_sale_date', 'Unknown')}
- Annual Taxes: {financial_info.get('tax_billed_amount', 'Unknown')}

LOCATION:
- County: {location_info.get('county', 'Unknown')}
- Metro: {location_info.get('cbsa_name', 'Unknown')}
        """
        
        return formatted.strip()

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for LLM"""
        formatted = []
        for msg in history:
            role = "You" if msg['role'] == 'assistant' else "User"
            formatted.append(f"{role}: {msg['content']}")
        return '\n'.join(formatted)

    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from analyst response"""
        questions = []
        sentences = text.split('?')
        for sentence in sentences[:-1]:  # Last split will be empty or not a question
            if sentence.strip():
                questions.append(sentence.strip() + '?')
        return questions[:3]  # Limit to 3 questions

    async def _call_llm(self, prompt: str, conversation_history: List[Dict] = None, property_context: str = None) -> str:
        """Call the LLM with system prompt, property context isolation, and conversation history"""
        
        # Enhanced system prompt with property context isolation
        enhanced_system_prompt = f"""
        {self.system_prompt}
        
        STRICT CONTEXT ISOLATION:
        {property_context or "Focus ONLY on the current property being analyzed."}
        
        FORBIDDEN ACTIONS:
        - Do NOT mention other addresses, properties, or locations
        - Do NOT use data from previous conversations about different properties  
        - Do NOT mix property details from different analyses
        - Do NOT use hardcoded facility data (like "2,875 sq ft, built 2000")
        
        REQUIRED: Use ONLY the exact property data provided in the current prompt.
        """
        
        messages = [{"role": "system", "content": enhanced_system_prompt}]
        
        if conversation_history:
            # Only include recent messages to avoid cross-contamination
            for msg in conversation_history[-5:]:  # Reduced to 5 messages for cleaner context
                messages.append({
                    "role": msg['role'], 
                    "content": msg['content']
                })
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.6,  # More focused responses
            max_tokens=800  # Increased for better formatted output
        )
        
        return response.choices[0].message.content
