import json
import re
from typing import Any, Dict, List, Union, Optional

class ResultExtractor:
    """
    Helper class to extract structured data from LLM responses.
    """
    
    @staticmethod
    def extract_json(text: str) -> Union[Dict, List, None]:
        """
        Robustly extract JSON object or array from text.
        """
        if not text:
            return None
            
        text = text.strip()
        
        # 1. Try to find markdown code blocks
        code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(code_block_pattern, text)
        for json_str in matches:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
        
        # 2. Try to find the first '{' and last '}' or '[' and ']'
        try:
            # Check for object
            start_obj = text.find('{')
            end_obj = text.rfind('}')
            
            # Check for array
            start_arr = text.find('[')
            end_arr = text.rfind(']')
            
            json_str = None
            
            # Heuristic: Determine if we are looking for an object or array based on what appears first
            is_object = False
            is_array = False
            
            if start_obj != -1 and end_obj != -1:
                is_object = True
            
            if start_arr != -1 and end_arr != -1:
                is_array = True
                
            if is_object and is_array:
                # If both are present, pick the one that starts earlier
                if start_arr < start_obj:
                    json_str = text[start_arr:end_arr+1]
                else:
                    json_str = text[start_obj:end_obj+1]
            elif is_object:
                json_str = text[start_obj:end_obj+1]
            elif is_array:
                json_str = text[start_arr:end_arr+1]
                
            if json_str:
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
            
        # 3. Last resort: try to parse the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
            
        return None

    @staticmethod
    def extract_key_value(text: str, key: str) -> Optional[str]:
        """
        Extract a value for a specific key from a text that might not be valid JSON.
        e.g., "Main Pattern: 正官格"
        """
        # Regex for "Key: Value" or "Key - Value"
        pattern = re.compile(f"{re.escape(key)}\s*[:：-]\s*(.+?)(?:\n|$)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return None
