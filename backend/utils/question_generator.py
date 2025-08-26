"""
Intelligent question generator for gathering missing transaction information.
Uses AI to ask contextually relevant questions based on current state.
"""
from langchain.prompts import ChatPromptTemplate
from backend.utils.model_selector import get_query_model
from backend.models.schemas import ActionDetails, DeFiAction
from typing import List, Dict, Any
from backend.logging_setup import logger

class QuestionGenerator:
    """Generates intelligent questions to gather missing transaction information."""
    
    @staticmethod
    def generate_next_question(action_details: ActionDetails, conversation_history: List[str] = None) -> Dict[str, Any]:
        """
        Generate the next intelligent question based on current transaction state.
        
        Args:
            action_details: Current action details
            conversation_history: Recent conversation for context
            
        Returns:
            Question with context and suggestions
        """
        # Get missing required fields
        completion_status = action_details.get_completion_status()
        missing_required = completion_status["missing_required"]
        
        if not missing_required:
            return {
                "question": "All required information collected! Ready to proceed?",
                "type": "confirmation",
                "suggestions": ["Yes, proceed", "Let me review", "Make changes"]
            }
        
        # Use AI to generate contextual question
        return QuestionGenerator._generate_ai_question(action_details, missing_required, conversation_history)
    
    @staticmethod
    def _generate_ai_question(action_details: ActionDetails, missing_fields: List[str], conversation_history: List[str] = None) -> Dict[str, Any]:
        """Use AI to generate contextually appropriate questions."""
        
        question_prompt = ChatPromptTemplate.from_template(
            """Current: {current_state}
Missing: {missing_fields}

Generate question JSON for first missing field:
{{
    "question": "conversational question",
    "field": "field_name",
    "suggestions": ["opt1", "opt2", "opt3"]
}}

Be helpful and concise."""
        )
        
        try:
            # Format current state
            current_state = QuestionGenerator._format_transaction_state(action_details)
            conversation_context = "\n".join(conversation_history[-3:]) if conversation_history else "No previous context"
            
            # Generate question using AI
            query_model = get_query_model()
            msg = question_prompt.format_messages(
                current_state=current_state,
                missing_fields=", ".join(missing_fields),
                conversation_context=conversation_context
            )
            
            response = query_model.invoke(msg)
            
            # Try to parse JSON response
            import json
            try:
                question_data = json.loads(response.content.strip())
                return question_data
            except json.JSONDecodeError:
                # Fallback to simple question
                return QuestionGenerator._generate_fallback_question(missing_fields[0])
                
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return QuestionGenerator._generate_fallback_question(missing_fields[0])
    
    @staticmethod
    def _format_transaction_state(action_details: ActionDetails) -> str:
        """Format current transaction state for AI context."""
        state_parts = []
        
        if action_details.action:
            state_parts.append(f"Action: {action_details.action.value}")
        if action_details.amount:
            state_parts.append(f"Amount: {action_details.amount}")
        if action_details.token_in:
            state_parts.append(f"From: {action_details.token_in}")
        if action_details.token_out:
            state_parts.append(f"To: {action_details.token_out}")
        if action_details.protocol:
            state_parts.append(f"Protocol: {action_details.protocol}")
        if action_details.slippage:
            state_parts.append(f"Slippage: {action_details.slippage}%")
        
        return ", ".join(state_parts) if state_parts else "No details collected yet"
    
    @staticmethod
    def _generate_fallback_question(missing_field: str) -> Dict[str, Any]:
        """Generate fallback questions when AI fails."""
        
        fallback_questions = {
            "action": {
                "question": "What DeFi action would you like to perform?",
                "type": "action_selection",
                "field": "action",
                "suggestions": ["Swap tokens", "Deposit/Lend", "Stake tokens", "Borrow"],
                "help_text": "Choose the type of DeFi transaction you want to make"
            },
            "amount": {
                "question": "How much would you like to transact?",
                "type": "amount_input",
                "field": "amount", 
                "suggestions": ["100", "0.5", "1000"],
                "help_text": "Enter the amount you want to use in the transaction"
            },
            "token_in": {
                "question": "Which token would you like to use?",
                "type": "token_selection",
                "field": "token_in",
                "suggestions": ["USDC", "ETH", "WBTC", "DAI"],
                "help_text": "Select the token you want to spend or deposit"
            },
            "token_out": {
                "question": "Which token would you like to receive?",
                "type": "token_selection", 
                "field": "token_out",
                "suggestions": ["ETH", "USDC", "WBTC", "DAI"],
                "help_text": "Select the token you want to receive"
            },
            "protocol": {
                "question": "Which DeFi protocol would you prefer?",
                "type": "protocol_selection",
                "field": "protocol",
                "suggestions": ["Uniswap", "Aave", "Compound", "Curve"],
                "help_text": "Choose the DeFi protocol to execute your transaction"
            }
        }
        
        return fallback_questions.get(missing_field, {
            "question": f"Please provide the {missing_field} for your transaction.",
            "type": "text_input",
            "field": missing_field,
            "suggestions": [],
            "help_text": f"This information is required to complete your transaction"
        })
    
    @staticmethod
    def generate_clarification_questions(action_details: ActionDetails) -> List[Dict[str, Any]]:
        """Generate multiple clarification questions for complex scenarios."""
        completion_status = action_details.get_completion_status()
        missing_required = completion_status["missing_required"]
        
        questions = []
        for field in missing_required[:3]:  # Limit to 3 questions
            question = QuestionGenerator._generate_fallback_question(field)
            questions.append(question)
        
        return questions