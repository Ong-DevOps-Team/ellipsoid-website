from openai import OpenAI
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))
# Add the project root directory to the path to access geo_ner module
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.settings import get_settings
from logging_system import error
from geo_ner import text_to_geotagged_text

# Get centralized default system prompt
settings = get_settings()
DEFAULT_SYSTEM_PROMPT = settings.DEFAULT_SYSTEM_PROMPT

class ChatbotService:
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = "gpt-4o"
        self.esri_api_key = getattr(self.settings, "esri_api_key", None)
        self.shipengine_api_key = getattr(self.settings, "shipengine_api_key", None)
        self.azure_language_key = getattr(self.settings, "azure_language_key", None)
        self.azure_language_endpoint = getattr(self.settings, "azure_language_endpoint", None)

    def _geo_enhance_text(self, raw_text: str, areas_of_interest: List[Dict[str, float]] = None) -> str:
        """
        Enhance text by converting geographic named entities to Geo-XML tags using GeoNER.
        Returns original text if enhancement fails or API keys are missing.
        """
        if not raw_text:
            return raw_text
        if not self.esri_api_key:
            return raw_text
        try:
            enhanced = text_to_geotagged_text(
                text_input=raw_text,
                api_keys={
                    "shipengine": self.shipengine_api_key,
                    "esri": self.esri_api_key,
                    "azure_language_key": self.azure_language_key,
                    "azure_language_endpoint": self.azure_language_endpoint
                },
                areas_of_interest=areas_of_interest
            )
            return enhanced or raw_text
        except Exception as e:
            return raw_text
    
    def chat(self, message: str, chat_history: list, areas_of_interest: List[Dict[str, float]] = None) -> dict:
        """
        Chat with GIS Expert AI with Geo-XML tagging support
        
        Args:
            message: User's input message
            chat_history: List of previous chat messages
            areas_of_interest: Optional list of area-of-interest bounds for geographic entity filtering
            
        Returns:
            dict: Contains 'text' (response), 'enhanced_user_message' (geo-enhanced input)
        
        Note: user_id is not currently used in this service, but can be accessed 
        via request.state.user_id in the calling endpoint if needed for future features.
        """
        try:
            # Enhance the input message with Geo-XML tagging
            enhanced_input = self._geo_enhance_text(message, areas_of_interest)
            
            # Determine which system prompt to use
            # Priority: 1) System prompt from chat_history, 2) Default fallback prompt
            if chat_history and len(chat_history) > 0:
                first_msg = chat_history[0]
                if hasattr(first_msg, 'role') and first_msg.role == 'system':
                    # Use the system prompt provided by the frontend (from MongoDB)
                    system_prompt = first_msg.content
                else:
                    # No system message found in chat history, use default
                    system_prompt = DEFAULT_SYSTEM_PROMPT
            else:
                # No chat history provided, use default
                system_prompt = DEFAULT_SYSTEM_PROMPT
            
            # Prepare messages array for OpenAI API
            # Start with the system prompt
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
            
            # Add conversation history (excluding system messages to avoid duplication)
            for msg in chat_history:
                if hasattr(msg, 'role') and msg.role != "system":
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Add the enhanced user message
            messages.append({
                "role": "user",
                "content": enhanced_input
            })
            
            # Send the complete conversation to OpenAI and get the response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
            )
            
            generated_text = response.choices[0].message.content
            
            # Enhance the response with Geo-XML tagging
            enhanced_response = self._geo_enhance_text(generated_text, areas_of_interest)
            
            return {
                'text': enhanced_response,
                'enhanced_user_message': enhanced_input
            }
            
        except Exception as e:
            error(f"Error in chatbot service: {e}")
            raise Exception(f"Chat failed: {str(e)}")
