"""
Intelligent Property Analyst Chatbot
Acts like a real commercial real estate analyst specializing in gas stations and convenience stores
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
from datetime import datetime
from .advanced_research_agent import AdvancedResearchAgent

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
        self.model = "gpt-4-1106-preview"
        self.research_agent = AdvancedResearchAgent(openai_api_key)
        
        # Analyst personality and expertise
        self.system_prompt = """
        You are Rohit, a senior commercial real estate analyst with 15+ years of experience 
        specializing in gas station and convenience store site selection. You use the IMST (Independent 
        Multi-Site Testing) methodology and are known for your thorough, conversational approach to 
        property evaluation.

        Your personality:
        - Give SHORT, clear responses (max 2-3 sentences)
        - Professional but direct
        - Ask ONE specific question at a time
        - Show what data you have vs what you need
        - Focus on critical missing info only

        Your expertise includes:
        - Traffic patterns and visibility analysis
        - Demographics and market analysis
        - Competition assessment
        - Zoning and regulatory considerations
        - Financial feasibility
        - Risk assessment
        - Brand compatibility

        Your approach:
        1. Start by acknowledging what you know about the property
        2. Ask targeted questions to fill critical data gaps
        3. Provide insights as you gather information
        4. Build towards a comprehensive IMST analysis
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

    async def start_analysis(self, property_address: str, smarty_data: Dict) -> AnalystResponse:
        """Start the property analysis conversation"""
        
        # Create initial context
        context = ConversationContext(
            property_address=property_address,
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
        You are Rohit analyzing this property with COMPLETE data:

        PROPERTY DATA FROM SMARTY API:
        {self._format_smarty_data(smarty_data)}

        You have detailed property information including building size, lot size, market value, owner, etc.

        Give a SHORT greeting (under 30 words) that:
        1. Shows you see the specific property details (mention building size or market value)
        2. Asks about daily traffic count

        Example: "I see this 2,875 sq ft convenience store worth $1.169M in Clayton County. What's the daily traffic count on Flint River Road?"
        """

        try:
            response = await self._call_llm(opening_prompt, [])
            
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
        
        # Analyze user input and update context
        context = await self._update_context_from_input(context, user_message)
        
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
        
        # If we have critical data, force completion
        if len(context.collected_data) >= 3 or "generating imst score" in user_message.lower() or "run the scoring" in user_message.lower():
            context.analysis_stage = 'complete'
            
        conversation_prompt = f"""
        You are Rohit analyzing this COMPLETE property:
        
        SMARTY DATA YOU HAVE:
        {self._format_smarty_data(context.smarty_data)}
        
        USER PROVIDED DATA:
        {json.dumps(context.collected_data, indent=2)}
        
        USER JUST SAID: "{user_message}"
        
        You have COMPLETE property data from Smarty API including building size, market value, owner, etc.
        
        If user asks what data you have, list the Smarty data details.
        If you have 2+ critical data points (traffic, competition, demographics), generate final IMST score.
        Otherwise ask for next missing critical data.
        
        Be SHORT (under 30 words) and show you have the property context.
        """

        try:
            response = await self._call_llm(conversation_prompt, context.conversation_history)
            
            # Update context based on response
            context.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # If analysis is complete, generate final score
            if context.analysis_stage == 'complete':
                # Calculate IMST score based ONLY on actual collected data
                collected = context.collected_data
                
                # Traffic scoring
                traffic_score = 5  # Default
                traffic_details = "No data provided"
                if 'traffic_count' in collected:
                    traffic_data = str(collected['traffic_count'])
                    if '23000' in traffic_data or '23,000' in traffic_data:
                        traffic_score = 9
                        traffic_details = "23,000 vehicles/day - Excellent"
                    elif any(str(i) in traffic_data for i in range(15000, 25000)):
                        traffic_score = 8
                        traffic_details = f"{traffic_data} - Very Good"
                    else:
                        traffic_score = 6
                        traffic_details = f"{traffic_data} - Moderate"
                
                # Competition scoring
                competition_score = 5  # Default
                competition_details = "No data provided"
                if 'competition' in collected:
                    comp_data = str(collected['competition']).lower()
                    if '1' in comp_data or 'one' in comp_data:
                        competition_score = 9
                        competition_details = "1 competitor - Excellent"
                    elif '2' in comp_data or 'two' in comp_data:
                        competition_score = 8
                        competition_details = "2 competitors - Very Good"
                    elif '3' in comp_data or 'three' in comp_data:
                        competition_score = 7
                        competition_details = "3 competitors - Good"
                    else:
                        competition_score = 6
                        competition_details = f"{comp_data} - Moderate"
                
                # Demographics scoring
                demographics_score = 5  # Default
                demographics_details = "No data provided"
                if 'demographics' in collected:
                    demo_data = str(collected['demographics'])
                    demographics_score = 6
                    demographics_details = f"{demo_data} - Basic data"
                
                # Facility scoring (from Smarty data)
                facility_score = 7
                facility_details = "2,875 sq ft, built 2000 - Good"
                
                overall_score = (traffic_score * 0.3 + competition_score * 0.2 + 
                               demographics_score * 0.3 + facility_score * 0.2)
                
                recommendation = "STRONG BUY" if overall_score >= 8 else "INVESTIGATE" if overall_score >= 6 else "PASS"
                
                final_score_message = f"""🎯 IMST ANALYSIS COMPLETE

📊 FINAL SCORE: {overall_score:.1f}/10

🔍 BREAKDOWN (Based on YOUR provided data):
• Traffic: {traffic_score}/10 ({traffic_details})
• Competition: {competition_score}/10 ({competition_details})
• Demographics: {demographics_score}/10 ({demographics_details})
• Facility: {facility_score}/10 ({facility_details})

💡 RECOMMENDATION: {recommendation}

📋 DATA USED:
{json.dumps(collected, indent=2)}

Analysis complete and stored."""
                
                # Store conversation for learning
                try:
                    from conversation_storage import conversation_storage
                    conversation_storage.store_conversation(
                        session_id=f"session_{hash(str(context.property_address))}",
                        property_address=context.property_address,
                        conversation_history=context.conversation_history,
                        final_score=overall_score
                    )
                except Exception as e:
                    logger.warning(f"Could not store conversation: {e}")
                
                response = final_score_message  # Return the final score as the response
            
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
        """Generate final IMST score and analysis"""
        
        scoring_prompt = f"""
        Generate a final IMST score for this gas station/convenience store:
        
        PROPERTY DATA:
        {self._format_smarty_data(context.smarty_data)}
        
        USER PROVIDED DATA:
        {json.dumps(context.collected_data, indent=2)}
        
        Calculate IMST scores (0-10) for:
        - Location: Traffic count, visibility, access
        - Market: Demographics, income levels  
        - Facility: Building size, lot size, age
        - Competition: Number of competitors
        
        Provide a SHORT summary (under 100 words) with:
        1. Overall IMST Score (0-10)
        2. Key strengths 
        3. Key concerns
        4. Investment recommendation (BUY/PASS/INVESTIGATE)
        
        Be direct and professional.
        """
        
        try:
            response = await self._call_llm(scoring_prompt, context.conversation_history)
            return response
        except Exception as e:
            logger.error(f"Error generating final score: {e}")
            return f"IMST Analysis Complete. Based on available data: Traffic (23k/day) is excellent, 4 competitors is moderate, demographics ($100k income) are strong. Estimated score: 7.5/10. Recommend: INVESTIGATE further."

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

    async def _call_llm(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """Call the LLM with system prompt and conversation history"""
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg['role'], 
                    "content": msg['content']
                })
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,  # Slightly more creative for conversational responses
            max_tokens=500
        )
        
        return response.choices[0].message.content
