import re
from datetime import datetime

def clean_json_response(response_text: str) -> str:
    """
    Clean and format the JSON response from Gemini
    
    Args:
        response_text (str): Raw response text from Gemini
        
    Returns:
        str: Cleaned JSON string
    """
    # Remove any text before the first {
    start_idx = response_text.find('{')
    if start_idx != -1:
        response_text = response_text[start_idx:]
    
    # Remove any text after the last }
    end_idx = response_text.rfind('}')
    if end_idx != -1:
        response_text = response_text[:end_idx + 1]
    
    return response_text

def format_date(date_str: str) -> str:
    """
    Format date string to a consistent format with time component
    
    Args:
        date_str (str): Input date string
        
    Returns:
        str: Formatted date string in ISO format with time
    """
    if not date_str:
        return "1970-01-01T00:00:00"  # Default date for empty strings
        
    try:
        # Try parsing common date formats
        for fmt in (
            '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d %H:%M:%S.%f'
        ):
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # Always return with time component
                return parsed_date.strftime('%Y-%m-%dT%H:%M:%S')
            except ValueError:
                continue
                
        # If no format matches, try to extract just the date part
        date_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})'
        match = re.search(date_pattern, date_str)
        if match:
            extracted_date = match.group(1)
            # Try parsing the extracted date
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y'):
                try:
                    parsed_date = datetime.strptime(extracted_date, fmt)
                    return parsed_date.strftime('%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    continue
                    
        return "1970-01-01T00:00:00"  # Default date if parsing fails
    except Exception:
        return "1970-01-01T00:00:00"  # Default date for any other errors 