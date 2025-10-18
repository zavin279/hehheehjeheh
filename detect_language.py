import re
from langdetect import detect, DetectorFactory

# Set seed for consistent results
DetectorFactory.seed = 0

def detect_script(text: str):
    """
    Enhanced language/script detection combining langdetect and script analysis
    """
    if not text or not text.strip():
        return "unknown"
    
    # Check for Telugu script (Unicode range U+0C00 to U+0C7F)
    if re.search(r'[\u0C00-\u0C7F]', text):
        return "telugu_native"
    
    # Check for Devanagari (Hindi) script (Unicode range U+0900 to U+097F)
    if re.search(r'[\u0900-\u097F]', text):
        return "hindi_native"
    
    # Check if it's mostly English (letters, numbers, common punctuation)
    if re.match(r'^[a-zA-Z0-9\s\.,!?;:\'\"-]+$', text.strip()):
        return "english"
    
    try:
        # Fall back to langdetect for romanized text
        lang = detect(text)
        
        if lang == "hi":
            return "hindi_roman"
        elif lang == "te":
            return "telugu_roman"
        elif lang == "en":
            return "english"
        
        return lang  # Return ISO code for other languages
        
    except Exception:
        # If detection fails, assume English if it has Latin characters
        if re.search(r'[a-zA-Z]', text):
            return "english"
        return "unknown"