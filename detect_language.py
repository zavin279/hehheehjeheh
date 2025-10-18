from langdetect import detect, DetectorFactory
# FIX: Renamed from detect_script to script_detector
from script_detector import detect_script as script_detect
import re
# Set seed for consistent results
DetectorFactory.seed = 0

def detect_script(text: str):
    """
    Enhanced language/script detection combining langdetect and script analysis
    """
    if not text or not text.strip():
        return "unknown"
    
    try:
        # First use script detection for accurate script identification
        script_result = script_detect(text)
        
        # If we got a definitive script result, refine it
        if script_result in ["telugu", "hindi"]:
            return f"{script_result}_native"
        elif script_result in ["roman-hindi", "roman-telugu"]:
            return script_result.replace("-", "_") + "_roman"
        elif script_result == "english":
             return "english"
        
        # Fall back to langdetect for unhandled or mixed cases
        lang = detect(text)
        
        if lang == "hi":
            # Check for native Devanagari characters
            if re.search(r'[\u0900-\u097F]', text): 
                return "hindi_native"
            return "hindi_roman"
        
        elif lang == "te":
            # Check for native Telugu characters
            if re.search(r'[\u0C00-\u0C7F]', text): 
                return "telugu_native"
            return "telugu_roman"

        return lang # Return ISO code for other languages
        
    except Exception:
        # If detection fails, assume basic Roman script if it looks like it
        if re.search(r'[a-zA-Z]', text):
            return "roman_fallback"
        return "unknown"
