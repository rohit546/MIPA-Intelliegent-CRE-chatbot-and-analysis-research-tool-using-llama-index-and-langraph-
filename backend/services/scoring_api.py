"""
API endpoints for the LLM-powered scoring system
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import logging
from .llm_scoring_system import LLMScoringSystem, ScoringResult

logger = logging.getLogger(__name__)

class ScoringRequest(BaseModel):
    property_data: Dict[str, Any]
    smarty_data: Optional[Dict[str, Any]] = None
    user_inputs: Optional[Dict[str, str]] = None

class UserQuestionResponse(BaseModel):
    question: str
    answer: str

class ScoringResponse(BaseModel):
    overall_score: float
    criteria_scores: Dict[str, float]
    confidence_level: str
    data_gaps: List[Dict[str, Any]]
    red_flags: List[str]
    recommendations: List[str]
    reasoning: str
    user_questions: List[str]
    analysis_timestamp: str

class ScoringAPI:
    """API wrapper for the LLM scoring system"""
    
    def __init__(self, openai_api_key: str):
        self.scoring_system = LLMScoringSystem(openai_api_key)
        self.active_sessions = {}  # Store active scoring sessions
    
    async def analyze_property(self, request: ScoringRequest) -> ScoringResponse:
        """Analyze a property and return scoring results"""
        try:
            logger.info(f"Starting property analysis for: {request.property_data.get('name', 'Unknown')}")
            
            # Perform the analysis
            result = await self.scoring_system.analyze_property(
                property_data=request.property_data,
                smarty_data=request.smarty_data
            )
            
            # Store session for potential follow-up questions
            session_id = f"session_{hash(str(request.property_data))}"
            self.active_sessions[session_id] = {
                'result': result,
                'property_data': request.property_data,
                'smarty_data': request.smarty_data
            }
            
            # Convert to response format
            response = self._convert_to_response(result, session_id)
            
            logger.info(f"Analysis completed with score: {result.overall_score}")
            return response
            
        except Exception as e:
            logger.error(f"Error in property analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    async def answer_question(self, session_id: str, response: UserQuestionResponse) -> ScoringResponse:
        """Process user's answer and update scoring if needed"""
        try:
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.active_sessions[session_id]
            original_result = session['result']
            
            # Update the scoring with user's answer
            updated_result = self.scoring_system.answer_user_question(
                original_result, response.question, response.answer
            )
            
            # Update session
            self.active_sessions[session_id]['result'] = updated_result
            
            return self._convert_to_response(updated_result, session_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing user answer: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")
    
    def _convert_to_response(self, result: ScoringResult, session_id: str) -> ScoringResponse:
        """Convert internal result to API response format"""
        from datetime import datetime
        
        return ScoringResponse(
            overall_score=result.overall_score,
            criteria_scores={
                "location": result.criteria_scores.location,
                "market": result.criteria_scores.market,
                "brand": result.criteria_scores.brand,
                "facility": result.criteria_scores.facility,
                "merchandising": result.criteria_scores.merchandising,
                "price": result.criteria_scores.price,
                "operations": result.criteria_scores.operations,
                "access_visibility": result.criteria_scores.access_visibility
            },
            confidence_level=result.confidence_level.value,
            data_gaps=[
                {
                    "field": gap.field,
                    "description": gap.description,
                    "confidence": gap.confidence.value,
                    "user_question": gap.user_question,
                    "suggested_sources": gap.suggested_sources or []
                }
                for gap in result.data_gaps
            ],
            red_flags=result.red_flags,
            recommendations=result.recommendations,
            reasoning=result.reasoning,
            user_questions=result.user_questions,
            analysis_timestamp=datetime.now().isoformat()
        )
