import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

class LLMRouter:
    def __init__(self):
        # We initialize models lazily or gracefully handle missing keys
        self.models = {}
        
        # Setup OpenAI (GPT-4o or GPT-3.5)
        if os.getenv("OPENAI_API_KEY"):
            self.models["openai"] = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            
        # Setup Anthropic (Claude 3 Haiku/Sonnet etc)
        if os.getenv("ANTHROPIC_API_KEY"):
            self.models["anthropic"] = ChatAnthropic(model_name="claude-3-haiku-20240307", temperature=0)
            
        # Setup Groq for lightning fast Llama 3
        if os.getenv("GROQ_API_KEY"):
            self.models["llama"] = ChatGroq(model_name="llama3-8b-8192", temperature=0)

    def process_message(self, text: str, provider: str = "openai", system_prompt: str = None) -> str:
        """Process a message using the specified LLM provider."""
        if provider not in self.models:
            return f"❌ Error: The '{provider}' model is not configured. Please check your API keys."
            
        chat_model = self.models[provider]
        
        messages = []
        if system_prompt:
             messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=text))
        
        try:
            response = chat_model.invoke(messages)
            return response.content
        except Exception as e:
            return f"❌ Validation Error communicating with {provider}: {str(e)}"
