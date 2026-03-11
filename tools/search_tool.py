from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

@tool
def web_search(query: str) -> str:
    """
    Search the internet for current events, facts, or information you don't know natively.
    Always use this when asked about recent news, current weather, or specific facts.
    
    Args:
        query: The search query string.
        
    Returns:
        The search results as a string.
    """
    try:
        return search.invoke(query)
    except Exception as e:
        return f"Error executing search: {str(e)}"
