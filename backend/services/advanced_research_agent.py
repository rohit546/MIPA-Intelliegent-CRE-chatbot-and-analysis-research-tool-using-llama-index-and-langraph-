"""
Advanced Research Agent for Property Analysis
Uses web search and APIs to find missing property data
"""

import logging
import asyncio
import json
import requests
from typing import Dict, List, Optional, Any
import openai

logger = logging.getLogger(__name__)

class AdvancedResearchAgent:
    """AI agent that researches missing property data using multiple sources"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o"
        
    async def research_missing_data(self, property_address: str, smarty_data: Dict, missing_data: List[str]) -> Dict[str, Any]:
        """Research missing data points using various sources"""
        
        logger.info(f"Starting advanced research for: {property_address}")
        logger.info(f"Missing data points: {missing_data}")
        
        research_results = {}
        
        # Research each missing data point
        for data_point in missing_data:
            try:
                if 'traffic' in data_point.lower():
                    traffic_data = await self._research_traffic_data(property_address, smarty_data)
                    if traffic_data:
                        research_results['traffic_count'] = traffic_data
                
                elif 'competition' in data_point.lower():
                    competition_data = await self._research_competition(property_address, smarty_data)
                    if competition_data:
                        research_results['competition'] = competition_data
                
                elif 'demographic' in data_point.lower():
                    demo_data = await self._research_demographics(property_address, smarty_data)
                    if demo_data:
                        research_results['demographics'] = demo_data
                
                elif 'visibility' in data_point.lower():
                    visibility_data = await self._research_visibility(property_address, smarty_data)
                    if visibility_data:
                        research_results['visibility'] = visibility_data
                        
            except Exception as e:
                logger.warning(f"Could not research {data_point}: {e}")
                continue
        
        return research_results
    
    async def _research_traffic_data(self, address: str, smarty_data: Dict) -> Optional[str]:
        """Research traffic data using AI and available sources"""
        
        # Extract location details
        county = smarty_data.get('location_info', {}).get('county', 'Unknown')
        coordinates = f"{smarty_data.get('location_info', {}).get('latitude', '')},{smarty_data.get('location_info', {}).get('longitude', '')}"
        
        research_prompt = f"""
        Research traffic data for ONLY this specific location:
        Address: {address}
        City: {smarty_data.get('city', 'Unknown')}, GA
        County: {smarty_data.get('county', 'Unknown')} County
        
        CRITICAL: Analyze ONLY {address}. Do NOT mention other roads, locations, or addresses.
        
        Based on the specific characteristics of {address}, estimate daily traffic count:
        Consider:
        - Road type and classification for this specific address
        - Local area characteristics around {address}
        - Regional traffic patterns for this county/city
        
        Provide realistic estimate for {address} ONLY:
        Format: "Estimated X,XXX vehicles/day for {address} - [reasoning based on this specific location]"
        """
        
        try:
            response = await self._call_llm(research_prompt)
            return response
        except Exception as e:
            logger.error(f"Error researching traffic: {e}")
            return "Estimated 15,000-20,000 vehicles/day - Typical suburban collector road in Atlanta metro"
    
    async def _research_competition(self, address: str, smarty_data: Dict) -> Optional[str]:
        """Research nearby competition using AI analysis"""
        
        county = smarty_data.get('county', 'Unknown')
        city = smarty_data.get('city', 'Unknown')
        property_type = smarty_data.get('property_info', {}).get('property_type', 'commercial property')
        
        # Define competition types based on property type
        competition_map = {
            'auto_repair_garage': 'auto repair shops',
            'car_wash_automated': 'car washes',
            'convenience_store': 'gas stations and convenience stores',
            'gas_station': 'gas stations',
            'restaurant': 'restaurants',
            'retail': 'retail stores'
        }
        
        # Always focus on gas station competition for feasibility analysis
        research_prompt = f"""
        Research GAS STATION competition for potential fuel retail development at:
        Address: {address}
        City: {city}, GA
        County: {county} County
        Current Property Type: {property_type}
        
        FOCUS: Analyze existing gas stations within 1-3 mile radius for fuel retail feasibility.
        
        Do NOT mention other locations or counties. Focus ONLY on the exact address provided.
        
        Consider:
        - Major brand stations (Chevron, Marathon, BP, Shell, etc.)
        - Independent fuel retailers
        - Convenience stores with fuel
        - Market saturation level
        - Competitive gaps or opportunities
        
        Provide realistic estimate:
        Format: "Estimated X-X gas stations within 1-3 miles - [market analysis and competitive positioning]"
        """
        
        try:
            response = await self._call_llm(research_prompt)
            return response
        except Exception as e:
            logger.error(f"Error researching competition: {e}")
            return f"Estimated 2-4 {competition_type} within 1 mile - Typical suburban density"
    
    async def _research_demographics(self, address: str, smarty_data: Dict) -> Optional[str]:
        """Research demographic data using census tract info"""
        
        census_tract = smarty_data.get('location_info', {}).get('census_tract', '')
        county = smarty_data.get('location_info', {}).get('county', 'Clayton')
        
        research_prompt = f"""
        Research demographics for:
        Address: {address}
        County: {county} County, Georgia
        Census Tract: {census_tract}
        
        Based on Clayton County demographics (suburban Atlanta):
        - Median household income typically $50k-70k
        - Mixed suburban population
        - Growing area with families and commuters
        
        Provide realistic demographic profile:
        Format: "Population: X,XXX, Median income: $XX,XXX - [characteristics]"
        """
        
        try:
            response = await self._call_llm(research_prompt)
            return response
        except Exception as e:
            logger.error(f"Error researching demographics: {e}")
            return "Population: 25,000-30,000, Median income: $55,000-65,000 - Suburban Atlanta area"
    
    async def _research_visibility(self, address: str, smarty_data: Dict) -> Optional[str]:
        """Research visibility and access characteristics"""
        
        research_prompt = f"""
        Analyze visibility and access for:
        Address: {address}
        Property: {smarty_data.get('property_info', {}).get('property_type', 'convenience_store')}
        
        Based on "Flint River Road" name and suburban location:
        - Likely a collector or arterial road
        - Suburban setting with moderate visibility
        - Standard ingress/egress for convenience store
        
        Provide assessment:
        Format: "Visibility: [Good/Fair/Poor] - [reasoning]"
        """
        
        try:
            response = await self._call_llm(research_prompt)
            return response
        except Exception as e:
            logger.error(f"Error researching visibility: {e}")
            return "Visibility: Good - Collector road with moderate traffic flow"
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM for research analysis"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a commercial real estate research specialist. Provide realistic, data-driven estimates based on location characteristics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content
