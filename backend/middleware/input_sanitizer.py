"""
Input sanitization middleware to prevent prompt injection and malicious inputs.
"""
import re
from backend.logging_setup import logger
from fastapi import HTTPException
from typing import Any, Dict

# Suspicious patterns that might indicate prompt injection
SUSPICIOUS_PATTERNS = [
    r'ignore\s+previous\s+instructions',
    r'forget\s+everything',
    r'system\s*:',
    r'assistant\s*:',
    r'human\s*:',
    r'<\s*script\s*>',
    r'javascript\s*:',
    r'eval\s*\(',
    r'exec\s*\(',
    r'\{\{\s*.*\s*\}\}',  # Template injection
    r'\$\{.*\}',  # Variable injection
]

# Compile patterns for better performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]

def sanitize_text_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text input to prevent prompt injection and other attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If input is malicious or too long
    """
    if not text:
        return text
    
    # Check length
    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input too long. Maximum {max_length} characters allowed."
        )
    
    # Check for suspicious patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Suspicious input detected: {text[:100]}...")
            raise HTTPException(
                status_code=400,
                detail="Input contains potentially malicious content."
            )
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text

def sanitize_dict_inputs(data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary inputs.
    
    Args:
        data: Dictionary to sanitize
        max_string_length: Maximum length for string values
        
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text_input(value, max_string_length)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_inputs(value, max_string_length)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_text_input(item, max_string_length) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

def validate_query_safety(query: str) -> bool:
    """
    Additional validation for query safety.
    
    Args:
        query: Query to validate
        
    Returns:
        True if query is safe, False otherwise
    """
    # Check for excessive repetition (potential DoS)
    words = query.split()
    if len(words) > 10:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
            if word_counts[word] > len(words) * 0.5:  # More than 50% repetition
                return False
    
    # Check for excessive special characters
    special_char_ratio = sum(1 for char in query if not char.isalnum() and char not in ' .,!?-') / len(query)
    if special_char_ratio > 0.3:  # More than 30% special characters
        return False
    
    return True