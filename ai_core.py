import google.generativeai as genai
from detect_language import detect_script 
from typing import Optional
from PIL import Image
import base64
import io
import openai
import os


class AIPersonality:
    """Handles interaction with Gemini and OpenAI APIs for generating responses with vision support."""
    
    def __init__(
        self, 
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        use_gemini: bool = True
    ):
        """
        Initialize AI with Gemini (primary) and OpenAI (fallback) support.
        """
        self.use_gemini = use_gemini
        self.model_name = "gemini-2.0-flash-exp" if use_gemini else "gpt-4o"
        
        # Fixed: Using environment variables properly
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if self.use_gemini:
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set.")
            genai.configure(api_key=self.gemini_api_key)
            # Fixed: Use GenerativeModel instead of Client
            self.model = genai.GenerativeModel(self.model_name)
        else:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set.")
            self.client = openai.OpenAI(api_key=self.openai_api_key)

    def _get_language_instruction(self, text: str) -> str:
        """Determines the language instruction for the AI model based on the script detected."""
        
        script = detect_script(text)
        
        if script == "telugu_native":
            return """**LANGUAGE INSTRUCTION:** The user typed in Telugu Script (తెలుగు). Reply in Telugu **Script (తెలుగు) ONLY**. Do not use Romanized language or other scripts."""
        
        elif script == "telugu_roman":
            return """**LANGUAGE INSTRUCTION:** The user typed in Romanized Telugu (e.g., 'ela unnav'). Reply in Romanized Telugu **ONLY**. Do not use Telugu Script or other languages."""
        
        elif script == "hindi_native":
            return """**LANGUAGE INSTRUCTION:** The user typed in Devanagari Script (Hindi). Reply in Devanagari Script (हिंदी) **ONLY**. Do not use Romanized language or other scripts."""
        
        elif script == "hindi_roman":
            return """**LANGUAGE INSTRUCTION:** The user typed in Romanized Hindi (e.g., 'kya hal hai'). Reply in Romanized Hindi **ONLY**. Do not use Devanagari Script or other languages."""
        
        elif script == "english":
            return """**LANGUAGE INSTRUCTION:** The user typed in English. Reply in English **only**. Do not use any other language, Romanized language (like Roman-Hindi or Roman-Telugu), or script."""
        
        else:
            return """**LANGUAGE INSTRUCTION:** Analyze the user's input. Identify the dominant language and script (e.g., English, Roman-Hindi, Telugu Script) and reply **EXCLUSIVELY** in that language and script. If the input is primarily English, reply **ONLY** in English."""
        

    def _generate_gemini_reply(self, system_prompt, user_input, image_path=None):
        """Generates a reply using the Google Gemini model."""
        
        # Prepare content list
        content_parts = []
        
        if image_path:
            try:
                img = Image.open(image_path)
                content_parts.append(img)
            except Exception as e:
                print(f"Error opening image: {e}")

        # Add text input
        content_parts.append(user_input)

        try:
            # Create a new chat with system instruction
            chat = self.model.start_chat(history=[])
            
            # Send message with system prompt included
            full_prompt = f"{system_prompt}\n\nUser: {user_input}"
            
            if image_path and content_parts:
                response = chat.send_message(content_parts)
            else:
                response = chat.send_message(full_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I encountered an API error while processing your request. Please try again."

    def _generate_openai_reply(self, system_prompt, user_input, image_path=None):
        """Generates a reply using the OpenAI model."""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        user_content = [{"type": "text", "text": user_input}]

        if image_path:
            print("Note: OpenAI vision models typically require a public URL or base64 encoding.")
            pass 

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "Sorry, I encountered an error while processing your request with OpenAI."

    def generate_ai_reply(self, user_input: str, personality: str, image_path: str = None):
        """
        Public method to generate the AI's reply.
        """
        # 1. Get Language Instruction
        lang_instruction = self._get_language_instruction(user_input)

        # 2. Construct System Prompt
        system_prompt = (
            f"You are an AI with the personality of a {personality}. "
            f"{lang_instruction} "
            "Maintain your persona strictly. Be concise and helpful."
        )

        # 3. Generate Reply
        if self.use_gemini:
            return self._generate_gemini_reply(system_prompt, user_input, image_path)
        else:
            return self._generate_openai_reply(system_prompt, user_input, image_path)