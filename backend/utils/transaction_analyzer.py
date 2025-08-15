"""
Transaction readiness analyzer for DeFi actions.
Determines when enough information is gathered to execute transactions.
"""
from typing import Dict, Any, List, Optional
from backend.models.schemas import ActionDetails, DeFiAction
import logging

logger = logging.getLogger(__name__)

class TransactionAnalyzer:
    """Analyzes transaction completeness and readiness for execution."""
    
    @staticmethod
    def analyze_readiness(action_details: ActionDetails) -> Dict[str, Any]:
        """
        Comprehensive analysis of transaction readiness.
        
        Args:
            action_details: Current action details
            
        Returns:
            Complete readiness analysis with next steps
        """
        completion_status = action_details.get_completion_status()
        
        # Enhanced analysis
        analysis = {
            **completion_status,
            "readiness_level": TransactionAnalyzer._get_readiness_level(completion_status),
            "user_guidance": TransactionAnalyzer._get_user_guidance(completion_status),
            "frontend_actions": TransactionAnalyzer._get_frontend_actions(completion_status),
            "validation_errors": TransactionAnalyzer._validate_transaction(action_details)
        }
        
        logger.info(f"Transaction readiness: {analysis['readiness_level']} "
                   f"({analysis['completion_percentage']}% complete)")
        
        return analysis
    
    @staticmethod
    def _get_readiness_level(completion_status: Dict[str, Any]) -> str:
        """Determine readiness level for frontend handling."""
        if completion_status["is_ready_for_execution"]:
            return "READY_FOR_CONFIRMATION"
        elif completion_status["completion_percentage"] >= 70:
            return "ALMOST_READY"
        elif completion_status["completion_percentage"] >= 40:
            return "PARTIALLY_COMPLETE"
        else:
            return "NEEDS_MORE_INFO"
    
    @staticmethod
    def _get_user_guidance(completion_status: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user guidance based on completion status."""
        if completion_status["is_ready_for_execution"]:
            return {
                "message": "All required information collected! Ready to proceed.",
                "action": "show_confirmation",
                "button_text": "Review & Confirm Transaction"
            }
        
        missing_count = len(completion_status["missing_required"])
        
        if missing_count == 1:
            return {
                "message": f"Just need one more detail: {completion_status['next_questions'][0]}",
                "action": "ask_question",
                "button_text": "Continue"
            }
        elif missing_count <= 3:
            return {
                "message": f"Need {missing_count} more details to proceed.",
                "action": "ask_questions",
                "button_text": "Continue Setup"
            }
        else:
            return {
                "message": "Let's gather the transaction details step by step.",
                "action": "start_wizard",
                "button_text": "Start Transaction Setup"
            }
    
    @staticmethod
    def _get_frontend_actions(completion_status: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific frontend actions and UI states."""
        readiness_level = TransactionAnalyzer._get_readiness_level(completion_status)
        
        frontend_actions = {
            "READY_FOR_CONFIRMATION": {
                "show_confirmation_modal": True,
                "enable_execute_button": True,
                "show_progress_bar": False,
                "highlight_complete_fields": True,
                "show_risk_warnings": True,
                "show_gas_estimate": True
            },
            "ALMOST_READY": {
                "show_confirmation_modal": False,
                "enable_execute_button": False,
                "show_progress_bar": True,
                "progress_percentage": completion_status["completion_percentage"],
                "highlight_missing_fields": completion_status["missing_required"],
                "show_next_question": True
            },
            "PARTIALLY_COMPLETE": {
                "show_confirmation_modal": False,
                "enable_execute_button": False,
                "show_progress_bar": True,
                "progress_percentage": completion_status["completion_percentage"],
                "show_wizard_steps": True,
                "current_step": TransactionAnalyzer._get_current_wizard_step(completion_status)
            },
            "NEEDS_MORE_INFO": {
                "show_confirmation_modal": False,
                "enable_execute_button": False,
                "show_progress_bar": True,
                "progress_percentage": completion_status["completion_percentage"],
                "show_getting_started": True,
                "suggested_actions": ["What would you like to do?", "Choose a DeFi action"]
            }
        }
        
        return frontend_actions.get(readiness_level, {})
    
    @staticmethod
    def _get_current_wizard_step(completion_status: Dict[str, Any]) -> int:
        """Determine current step in transaction wizard."""
        missing_required = completion_status["missing_required"]
        
        if "action" in missing_required:
            return 1  # Choose action
        elif "amount" in missing_required:
            return 2  # Enter amount
        elif any(field in missing_required for field in ["token_in", "token_out"]):
            return 3  # Select tokens
        elif "protocol" in missing_required:
            return 4  # Choose protocol
        else:
            return 5  # Final details
    
    @staticmethod
    def _validate_transaction(action_details: ActionDetails) -> List[str]:
        """Validate transaction details for potential issues."""
        errors = []
        
        # Amount validation
        if action_details.amount:
            try:
                amount_val = float(action_details.amount)
                if amount_val <= 0:
                    errors.append("Amount must be greater than zero")
                elif amount_val > 1000000:
                    errors.append("Amount seems unusually large - please verify")
            except (ValueError, TypeError):
                errors.append("Invalid amount format")
        
        # Token validation for swaps
        if action_details.action == DeFiAction.SWAP:
            if action_details.token_in == action_details.token_out:
                errors.append("Cannot swap a token for itself")
        
        # Slippage validation
        if action_details.slippage:
            if action_details.slippage < 0.1:
                errors.append("Slippage tolerance too low - transaction may fail")
            elif action_details.slippage > 50:
                errors.append("Slippage tolerance too high - risk of significant loss")
        
        return errors
    
    @staticmethod
    def generate_confirmation_summary(action_details: ActionDetails) -> Dict[str, Any]:
        """Generate detailed confirmation summary for user review."""
        completion_status = action_details.get_completion_status()
        
        if not completion_status["is_ready_for_execution"]:
            return {"error": "Transaction not ready for confirmation"}
        
        return {
            "transaction_summary": {
                "action": action_details.action.value if action_details.action else "Unknown",
                "description": completion_status["confirmation_message"],
                "amount": action_details.amount,
                "tokens": {
                    "from": action_details.token_in,
                    "to": action_details.token_out
                },
                "protocol": action_details.protocol,
                "estimated_gas": completion_status["estimated_gas"]
            },
            "transaction_details": {
                "slippage_tolerance": f"{action_details.slippage}%" if action_details.slippage else "Default (0.5%)",
                "deadline": f"{action_details.deadline} seconds" if action_details.deadline else "Default (1200s)",
                "gas_price": action_details.gas_price or "Market rate"
            },
            "risk_assessment": {
                "warnings": completion_status["risk_warnings"],
                "risk_level": TransactionAnalyzer._assess_risk_level(action_details),
                "recommendations": TransactionAnalyzer._get_risk_recommendations(action_details)
            },
            "next_steps": [
                "Review all transaction details carefully",
                "Ensure you have sufficient balance and gas",
                "Confirm the transaction in your wallet",
                "Wait for blockchain confirmation"
            ]
        }
    
    @staticmethod
    def _assess_risk_level(action_details: ActionDetails) -> str:
        """Assess overall risk level of the transaction."""
        risk_factors = 0
        
        # High amount
        if action_details.amount:
            try:
                if float(action_details.amount) > 10000:
                    risk_factors += 2
                elif float(action_details.amount) > 1000:
                    risk_factors += 1
            except (ValueError, TypeError):
                pass
        
        # High slippage
        if action_details.slippage and action_details.slippage > 5:
            risk_factors += 2
        elif action_details.slippage and action_details.slippage > 2:
            risk_factors += 1
        
        # Complex actions
        if action_details.action in [DeFiAction.BORROW, DeFiAction.LEND]:
            risk_factors += 1
        
        if risk_factors >= 4:
            return "HIGH"
        elif risk_factors >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def _get_risk_recommendations(action_details: ActionDetails) -> List[str]:
        """Get risk mitigation recommendations."""
        recommendations = []
        
        if action_details.action == DeFiAction.SWAP:
            recommendations.append("Consider the current market volatility")
            recommendations.append("Check token liquidity before large swaps")
        
        if action_details.action in [DeFiAction.LEND, DeFiAction.BORROW]:
            recommendations.append("Understand the liquidation risks")
            recommendations.append("Monitor your health factor regularly")
        
        recommendations.append("Always verify contract addresses")
        recommendations.append("Start with smaller amounts for new protocols")
        
        return recommendations