import os
import urllib3
urllib3.disable_warnings()
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Import our custom tools
from tools.datetime_tool import get_current_datetime
from tools.search_tool import web_search

class LLMRouter:
    def __init__(self):
        # Dictionary to store chat histories per user ID
        self.user_histories: Dict[str, BaseChatMessageHistory] = {}
        
        # Tools available to the agent
        self.tools = [get_current_datetime, web_search]
        
        # We initialize models lazily or gracefully handle missing keys
        self.models = {}
        
        # Setup OpenAI (GPT-4o or GPT-3.5)
        if os.getenv("OPENAI_API_KEY"):
            # Using gpt-4o-mini as a fast/cheap reliable agent model, or gpt-3.5-turbo
            self.models["openai"] = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
        # Setup Anthropic (Claude 3 Haiku/Sonnet etc)
        if os.getenv("ANTHROPIC_API_KEY"):
            self.models["anthropic"] = ChatAnthropic(model_name="claude-3-haiku-20240307", temperature=0)
            
        # Setup Groq for lightning fast Llama 3
        if os.getenv("GROQ_API_KEY"):
            # Llama 3 70b is much better at tool calling than 8b
            self.models["llama"] = ChatGroq(model_name="llama3-70b-8192", temperature=0)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create a chat history for a specific user session."""
        if session_id not in self.user_histories:
            self.user_histories[session_id] = ChatMessageHistory()
        return self.user_histories[session_id]

    def process_message(self, text: str, user_id: str, provider: str = "openai", system_prompt: str = None) -> str:
        """Process a message using the specified LLM provider with tools and memory."""
        if provider not in self.models:
            return f"❌ Error: The '{provider}' model is not configured. Please check your API keys."
            
        chat_model = self.models[provider]
        
        # 1. Define the Prompt Template (System prompt + History + New Message + Agent Scratchpad)
        sys_prompt = system_prompt or "You are a helpful, smart personal assistant. Use the tools provided to answer the user's questions or execute tasks. If you don't need a tool, just answer normally."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 2. Create the Agent
        try:
            agent = create_tool_calling_agent(chat_model, self.tools, prompt)
            
            # 3. Create the Agent Executor (Runs the agent loop)
            agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            # 4. Wrap with Memory History
            agent_with_chat_history = RunnableWithMessageHistory(
                agent_executor,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            
            # 5. Execute
            response = agent_with_chat_history.invoke(
                {"input": text},
                config={"configurable": {"session_id": str(user_id)}}
            )
            
            return response["output"]
            
        except Exception as e:
            return f"❌ Agent Error communicating with {provider}: {str(e)}"
