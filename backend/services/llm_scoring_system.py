"""
LLM-Powered IMST Scoring System
Implements intelligent property scoring with agentic data completion
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
from datetime import datetime
import asyncio
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

@dataclass
class ScoringCriteria:
    """IMST Scoring Criteria based on the 7-Elements+ system"""
    location: float = 0.0  # 25% weight
    market: float = 0.0    # 20% weight
    brand: float = 0.0     # 15% weight
    facility: float = 0.0  # 15% weight
    merchandising: float = 0.0  # 10% weight
    price: float = 0.0     # 5% weight
    operations: float = 0.0  # 5% weight
    access_visibility: float = 0.0  # 5% weight
    
    # Additional criteria
    competition_intensity: float = 0.0
    diesel_truck_program: float = 0.0
    digital_loyalty: float = 0.0
    entitlement_risk: float = 0.0

@dataclass
class DataGap:
    """Represents missing or uncertain data"""
    field: str
    description: str
    confidence: ConfidenceLevel
    user_question: Optional[str] = None
    suggested_sources: List[str] = None

@dataclass
class ScoringResult:
    """Complete scoring analysis result"""
    overall_score: float
    criteria_scores: ScoringCriteria
    confidence_level: ConfidenceLevel
    data_gaps: List[DataGap]
    red_flags: List[str]
    recommendations: List[str]
    reasoning: str
    user_questions: List[str]

class LLMScoringSystem:
    """LLM-powered property scoring with agentic capabilities"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = "gpt-4-1106-preview"  # Can be upgraded to GPT-5 when available
        
        # IMST scoring weights
        self.weights = {
            "location": 0.25,
            "market": 0.20,
            "brand": 0.15,
            "facility": 0.15,
            "merchandising": 0.10,
            "price": 0.05,
            "operations": 0.05,
            "access_visibility": 0.05
        }
        
        # Red flags that immediately disqualify properties
        self.red_flags_criteria = [
            "Environmental contamination",
            "Zoning restrictions preventing gas station",
            "Traffic count below 10,000 vehicles/day",
            "No highway visibility",
            "Flood zone restrictions",
            "Competitor within 0.25 miles with superior positioning"
        ]

    async def analyze_property(self, property_data: Dict, smarty_data: Dict = None) -> ScoringResult:
        """Main analysis function that orchestrates the scoring process"""
        logger.info(f"Starting property analysis for: {property_data.get('name', 'Unknown')}")
        
        # Step 1: Initial data assessment
        enhanced_data = await self._enhance_property_data(property_data, smarty_data)
        
        # Step 2: Identify data gaps
        data_gaps = await self._identify_data_gaps(enhanced_data)
        
        # Step 3: Attempt to fill gaps using available APIs
        filled_data = await self._fill_data_gaps(enhanced_data, data_gaps)
        
        # Step 4: Generate user questions for remaining gaps
        user_questions = await self._generate_user_questions(data_gaps)
        
        # Step 5: Perform IMST scoring
        scoring_result = await self._perform_imst_scoring(filled_data, data_gaps)
        
        return scoring_result

    async def _enhance_property_data(self, property_data: Dict, smarty_data: Dict = None) -> Dict:
        """Enhance property data using LLM reasoning and external APIs"""
        
        enhancement_prompt = f"""
        As a commercial real estate expert specializing in gas station and convenience store site selection,
        analyze the following property data and enhance it with relevant insights.

        Property Data: {json.dumps(property_data, indent=2)}
        Smarty Data: {json.dumps(smarty_data or {}, indent=2)}

        Please provide enhanced analysis including:
        1. Market positioning assessment
        2. Location advantages/disadvantages
        3. Competition analysis (if data available)
        4. Traffic pattern insights
        5. Demographic suitability
        6. Potential challenges or opportunities

        Format your response as structured JSON with clear categories.
        """

        try:
            response = await self._call_llm(enhancement_prompt)
            enhanced_insights = json.loads(response)
            
            # Merge enhanced insights with original data
            enhanced_data = {**property_data}
            enhanced_data['llm_insights'] = enhanced_insights
            enhanced_data['smarty_data'] = smarty_data or {}
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing property data: {e}")
            return {**property_data, 'smarty_data': smarty_data or {}}

    async def _identify_data_gaps(self, enhanced_data: Dict) -> List[DataGap]:
        """Identify missing data critical for IMST scoring"""
        
        gap_analysis_prompt = f"""
        Analyze the following property data for the IMST (Independent Multi-Site Testing) scoring system.
        Identify critical missing data points needed for accurate gas station/convenience store site evaluation.

        Property Data: {json.dumps(enhanced_data, indent=2)}

        Required IMST Data Points:
        - Traffic counts (vehicles per day)
        - Demographics (income, age, household size)
        - Competition analysis (nearby gas stations, convenience stores)
        - Visibility and access (highway visibility, ingress/egress)
        - Market characteristics (population density, growth trends)
        - Zoning and regulatory constraints
        - Environmental factors
        - Brand compatibility
        - Fuel delivery logistics

        For each missing critical data point, provide:
        1. Field name
        2. Description of why it's important
        3. Confidence level in current data
        4. Suggested question to ask the user
        5. Alternative data sources

        Return as JSON array of data gaps.
        """

        try:
            response = await self._call_llm(gap_analysis_prompt)
            gaps_data = json.loads(response)
            
            data_gaps = []
            for gap in gaps_data:
                data_gaps.append(DataGap(
                    field=gap.get('field', ''),
                    description=gap.get('description', ''),
                    confidence=ConfidenceLevel(gap.get('confidence', 'unknown')),
                    user_question=gap.get('user_question'),
                    suggested_sources=gap.get('suggested_sources', [])
                ))
            
            return data_gaps
            
        except Exception as e:
            logger.error(f"Error identifying data gaps: {e}")
            return []

    async def _fill_data_gaps(self, enhanced_data: Dict, data_gaps: List[DataGap]) -> Dict:
        """Attempt to fill data gaps using available APIs and web search"""
        
        filled_data = enhanced_data.copy()
        
        # Extract location information
        address_info = enhanced_data.get('address', {})
        location = f"{address_info.get('street', '')}, {address_info.get('city', '')}, {address_info.get('state', '')}"
        
        # Try to fill gaps using various methods
        for gap in data_gaps:
            try:
                if 'traffic' in gap.field.lower():
                    # Attempt to get traffic data
                    traffic_data = await self._get_traffic_data(location)
                    if traffic_data:
                        filled_data[f'estimated_{gap.field}'] = traffic_data
                
                elif 'demographic' in gap.field.lower():
                    # Use census data if available
                    demo_data = await self._get_demographic_data(location)
                    if demo_data:
                        filled_data[f'estimated_{gap.field}'] = demo_data
                
                elif 'competition' in gap.field.lower():
                    # Search for nearby competitors
                    competitors = await self._find_nearby_competitors(location)
                    if competitors:
                        filled_data['nearby_competitors'] = competitors
                        
            except Exception as e:
                logger.warning(f"Could not fill data gap for {gap.field}: {e}")
                continue
        
        return filled_data

    async def _generate_user_questions(self, data_gaps: List[DataGap]) -> List[str]:
        """Generate intelligent questions to ask the user for missing data"""
        
        high_priority_gaps = [gap for gap in data_gaps if gap.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.UNKNOWN]]
        
        questions = []
        for gap in high_priority_gaps[:5]:  # Limit to top 5 questions
            if gap.user_question:
                questions.append(gap.user_question)
        
        return questions

    async def _perform_imst_scoring(self, filled_data: Dict, data_gaps: List[DataGap]) -> ScoringResult:
        """Perform the IMST scoring using LLM reasoning"""
        
        scoring_prompt = f"""
        As an expert in gas station and convenience store site selection using the IMST methodology,
        perform a comprehensive scoring analysis of this property.

        Property Data: {json.dumps(filled_data, indent=2)}
        Data Gaps: {[gap.field for gap in data_gaps]}

        IMST Scoring Criteria (out of 10 points each):
        1. LOCATION (25% weight): Highway access, visibility, traffic patterns, corner positioning
        2. MARKET (20% weight): Demographics, income levels, population density, growth trends
        3. BRAND (15% weight): Brand compatibility, market presence, competitive positioning
        4. FACILITY (15% weight): Site size, layout potential, infrastructure, environmental
        5. MERCHANDISING (10% weight): Local preferences, product mix opportunities
        6. PRICE (5% weight): Fuel pricing competitiveness, market dynamics
        7. OPERATIONS (5% weight): Staffing, logistics, operational efficiency
        8. ACCESS & VISIBILITY (5% weight): Ingress/egress, signage, highway visibility

        Additional Considerations:
        - Competition intensity
        - Diesel/truck program potential
        - Digital & loyalty program opportunities
        - Entitlement/execution risks

        Red Flags (immediate disqualifiers):
        - Environmental issues
        - Zoning restrictions
        - Poor traffic counts (<10,000 VPD)
        - Superior competitor within 0.25 miles

        Provide:
        1. Individual scores for each criterion (0-10)
        2. Overall weighted score (0-10)
        3. Confidence level assessment
        4. Identified red flags
        5. Specific recommendations
        6. Detailed reasoning for each score
        7. Risk assessment

        Return as structured JSON.
        """

        try:
            response = await self._call_llm(scoring_prompt)
            scoring_data = json.loads(response)
            
            # Extract scores
            criteria_scores = ScoringCriteria(
                location=scoring_data.get('scores', {}).get('location', 0),
                market=scoring_data.get('scores', {}).get('market', 0),
                brand=scoring_data.get('scores', {}).get('brand', 0),
                facility=scoring_data.get('scores', {}).get('facility', 0),
                merchandising=scoring_data.get('scores', {}).get('merchandising', 0),
                price=scoring_data.get('scores', {}).get('price', 0),
                operations=scoring_data.get('scores', {}).get('operations', 0),
                access_visibility=scoring_data.get('scores', {}).get('access_visibility', 0)
            )
            
            # Generate user questions for remaining gaps
            user_questions = await self._generate_user_questions(data_gaps)
            
            return ScoringResult(
                overall_score=scoring_data.get('overall_score', 0),
                criteria_scores=criteria_scores,
                confidence_level=ConfidenceLevel(scoring_data.get('confidence_level', 'medium')),
                data_gaps=data_gaps,
                red_flags=scoring_data.get('red_flags', []),
                recommendations=scoring_data.get('recommendations', []),
                reasoning=scoring_data.get('reasoning', ''),
                user_questions=user_questions
            )
            
        except Exception as e:
            logger.error(f"Error performing IMST scoring: {e}")
            return ScoringResult(
                overall_score=0,
                criteria_scores=ScoringCriteria(),
                confidence_level=ConfidenceLevel.LOW,
                data_gaps=data_gaps,
                red_flags=["Error in analysis"],
                recommendations=["Manual review required"],
                reasoning="Analysis failed due to technical error",
                user_questions=[]
            )

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM API with error handling"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert commercial real estate analyst specializing in gas station and convenience store site selection using the IMST methodology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    async def _get_traffic_data(self, location: str) -> Optional[Dict]:
        """Attempt to get traffic data from available sources"""
        # This would integrate with traffic data APIs
        # For now, return None to indicate data not available
        return None

    async def _get_demographic_data(self, location: str) -> Optional[Dict]:
        """Get demographic data from census or other sources"""
        # This would integrate with census APIs
        return None

    async def _find_nearby_competitors(self, location: str) -> Optional[List[Dict]]:
        """Find nearby gas stations and convenience stores"""
        # This would integrate with Google Places API or similar
        return None

    def answer_user_question(self, scoring_result: ScoringResult, question: str, answer: str) -> ScoringResult:
        """Update scoring based on user's answer to a question"""
        # This would re-run the scoring with the additional information
        # For now, return the original result
        logger.info(f"User answered: {question} -> {answer}")
        return scoring_result
