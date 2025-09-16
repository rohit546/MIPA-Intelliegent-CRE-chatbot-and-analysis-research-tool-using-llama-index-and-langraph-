"""
Simple conversation storage for feedback and improvement
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class ConversationStorage:
    """Store and retrieve conversation data for analysis and improvement"""
    
    def __init__(self, storage_file="conversations.json"):
        self.storage_file = storage_file
        self.conversations = self._load_conversations()
    
    def _load_conversations(self) -> List[Dict]:
        """Load existing conversations from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_conversations(self):
        """Save conversations to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            print(f"Error saving conversations: {e}")
    
    def store_conversation(self, session_id: str, property_address: str, 
                          conversation_history: List[Dict], final_score: float = None):
        """Store a complete conversation"""
        conversation_data = {
            "session_id": session_id,
            "property_address": property_address,
            "timestamp": datetime.now().isoformat(),
            "conversation_history": conversation_history,
            "final_score": final_score,
            "message_count": len(conversation_history),
            "duration_minutes": self._calculate_duration(conversation_history)
        }
        
        self.conversations.append(conversation_data)
        self._save_conversations()
    
    def _calculate_duration(self, history: List[Dict]) -> float:
        """Calculate conversation duration in minutes"""
        if len(history) < 2:
            return 0
        
        try:
            start_time = datetime.fromisoformat(history[0]['timestamp'])
            end_time = datetime.fromisoformat(history[-1]['timestamp'])
            return (end_time - start_time).total_seconds() / 60
        except:
            return 0
    
    def get_feedback_insights(self) -> Dict:
        """Get insights from stored conversations for system improvement"""
        if not self.conversations:
            return {"total_conversations": 0}
        
        total = len(self.conversations)
        avg_messages = sum(c['message_count'] for c in self.conversations) / total
        avg_duration = sum(c['duration_minutes'] for c in self.conversations) / total
        
        return {
            "total_conversations": total,
            "average_messages_per_conversation": round(avg_messages, 1),
            "average_duration_minutes": round(avg_duration, 1),
            "recent_properties": [c['property_address'] for c in self.conversations[-5:]]
        }

# Global storage instance
conversation_storage = ConversationStorage()
