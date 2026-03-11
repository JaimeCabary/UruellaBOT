import os
from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# Import our custom tools
from tools.datetime_tool import get_current_datetime
from tools.search_tool import web_search


class LLMRouter:
    def __init__(self):
        # Dictionary to store conversation histories per user ID (in-memory)
        self.user_histories: Dict[str, list] = {}

        # Tools available to the agent
        self.tools = [get_current_datetime, web_search]

        # We initialize models lazily or gracefully handle missing keys
        self.models = {}

        if os.getenv("OPENAI_API_KEY"):
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            self.models["openai"] = llm.bind_tools(self.tools)

        if os.getenv("ANTHROPIC_API_KEY"):
            llm = ChatAnthropic(model_name="claude-3-haiku-20240307", temperature=0)
            self.models["anthropic"] = llm.bind_tools(self.tools)

        if os.getenv("GROQ_API_KEY"):
            llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)
            self.models["llama"] = llm.bind_tools(self.tools)

        # Map tool names to functions for execution
        self.tool_map = {t.name: t for t in self.tools}

    def _get_history(self, user_id: str) -> list:
        if user_id not in self.user_histories:
            self.user_histories[user_id] = []
        return self.user_histories[user_id]

    def process_message(self, text: str, user_id: str, provider: str = "openai", system_prompt: str = None) -> str:
        """Process a message using the specified LLM provider with tools and memory."""
        if provider not in self.models:
            return f"❌ Error: The '{provider}' model is not configured. Please check your API keys."

        chat_model = self.models[provider]
        history = self._get_history(user_id)

        sys_prompt = system_prompt or (
            "You are Uruella, a brilliant and helpful personal assistant. "
            "You have access to tools to search the web and check the current time. "
            "Use them proactively when needed. Be concise, smart and friendly."
        )

        # Build the messages list: system prompt + history + new message
        messages = [SystemMessage(content=sys_prompt)] + history + [HumanMessage(content=text)]

        try:
            # First call: ask the LLM (may trigger a tool call)
            response = chat_model.invoke(messages)

            # If the LLM wants to call a tool, execute it and call again
            if response.tool_calls:
                tool_results = []
                for tc in response.tool_calls:
                    tool_fn = self.tool_map.get(tc["name"])
                    if tool_fn:
                        result = tool_fn.invoke(tc["args"])
                        from langchain_core.messages import ToolMessage
                        tool_results.append(ToolMessage(
                            content=str(result),
                            tool_call_id=tc["id"]
                        ))

                # Second call: give LLM the tool results to form final reply
                messages = messages + [response] + tool_results
                response = chat_model.invoke(messages)

            # Save to history (keep last 20 messages to avoid token overflow)
            history.append(HumanMessage(content=text))
            history.append(AIMessage(content=response.content))
            if len(history) > 20:
                self.user_histories[user_id] = history[-20:]

            return response.content

        except Exception as e:
            return f"❌ Error: {str(e)}"
