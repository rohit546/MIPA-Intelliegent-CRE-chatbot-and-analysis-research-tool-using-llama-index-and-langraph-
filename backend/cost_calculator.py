"""
Cost Calculator for IMST Analysis System
Calculates API costs for GPT-4 usage in property analysis
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CostCalculator:
    """Calculate costs for GPT-4 API usage in property analysis"""
    
    def __init__(self):
        # GPT-4 Turbo pricing (as of 2024)
        self.gpt4_turbo_input_cost = 0.01 / 1000   # $0.01 per 1K input tokens
        self.gpt4_turbo_output_cost = 0.03 / 1000  # $0.03 per 1K output tokens
        
        # Estimated token usage per research operation
        self.token_estimates = {
            'start_analysis': {
                'input': 500,   # Property data + system prompt
                'output': 100   # Short greeting
            },
            'continue_conversation': {
                'input': 300,   # Context + user message
                'output': 50    # Short response
            },
            'research_traffic': {
                'input': 400,   # Location data + research prompt
                'output': 200   # Detailed traffic analysis
            },
            'research_competition': {
                'input': 300,   # Location + competition prompt
                'output': 150   # Competition analysis
            },
            'research_demographics': {
                'input': 300,   # Census + location data
                'output': 200   # Demographic profile
            },
            'research_visibility': {
                'input': 250,   # Property + visibility prompt
                'output': 100   # Visibility assessment
            },
            'final_scoring': {
                'input': 800,   # All collected data + scoring prompt
                'output': 300   # Complete IMST analysis
            }
        }
    
    def calculate_research_cost(self, research_operations: List[str]) -> Dict[str, float]:
        """Calculate cost for a complete research session"""
        
        total_input_tokens = 0
        total_output_tokens = 0
        operation_costs = {}
        
        for operation in research_operations:
            if operation in self.token_estimates:
                est = self.token_estimates[operation]
                input_tokens = est['input']
                output_tokens = est['output']
                
                input_cost = input_tokens * self.gpt4_turbo_input_cost
                output_cost = output_tokens * self.gpt4_turbo_output_cost
                operation_cost = input_cost + output_cost
                
                operation_costs[operation] = {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'input_cost': input_cost,
                    'output_cost': output_cost,
                    'total_cost': operation_cost
                }
                
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
        
        total_input_cost = total_input_tokens * self.gpt4_turbo_input_cost
        total_output_cost = total_output_tokens * self.gpt4_turbo_output_cost
        total_cost = total_input_cost + total_output_cost
        
        return {
            'total_cost': total_cost,
            'total_input_cost': total_input_cost,
            'total_output_cost': total_output_cost,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'operation_breakdown': operation_costs,
            'cost_per_1k_tokens': {
                'input': self.gpt4_turbo_input_cost * 1000,
                'output': self.gpt4_turbo_output_cost * 1000
            }
        }
    
    def estimate_full_analysis_cost(self) -> Dict[str, float]:
        """Estimate cost for a complete property analysis"""
        
        # Typical full analysis operations
        full_analysis = [
            'start_analysis',
            'continue_conversation',  # 2-3 user interactions
            'continue_conversation',
            'continue_conversation',
            'research_traffic',
            'research_competition',
            'research_demographics', 
            'research_visibility',
            'final_scoring'
        ]
        
        return self.calculate_research_cost(full_analysis)
    
    def estimate_research_only_cost(self) -> Dict[str, float]:
        """Estimate cost for research-only mode"""
        
        research_only = [
            'start_analysis',
            'research_traffic',
            'research_competition',
            'research_demographics',
            'research_visibility',
            'final_scoring'
        ]
        
        return self.calculate_research_only_cost(research_only)
    
    def format_cost_report(self, cost_data: Dict) -> str:
        """Format cost data into readable report"""
        
        report = f"""
💰 COST ANALYSIS REPORT

🔍 TOTAL COST: ${cost_data['total_cost']:.4f}

📊 TOKEN USAGE:
• Input Tokens: {cost_data['total_input_tokens']:,} (${cost_data['total_input_cost']:.4f})
• Output Tokens: {cost_data['total_output_tokens']:,} (${cost_data['total_output_cost']:.4f})

💡 COST BREAKDOWN:
"""
        
        for operation, details in cost_data['operation_breakdown'].items():
            report += f"• {operation}: ${details['total_cost']:.4f}\n"
        
        report += f"""
📈 PRICING:
• Input: ${cost_data['cost_per_1k_tokens']['input']:.2f} per 1K tokens
• Output: ${cost_data['cost_per_1k_tokens']['output']:.2f} per 1K tokens

⏱️ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report.strip()

# Global cost calculator instance
cost_calculator = CostCalculator()
