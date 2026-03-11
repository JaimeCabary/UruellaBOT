import sys
print(f"Python version: {sys.version}")

try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
except ImportError:
    print("Langchain not installed")

try:
    from langchain.agents import create_tool_calling_agent
    print("SUCCESS: create_tool_calling_agent imported successfully!")
except ImportError as e:
    print(f"ERROR importing create_tool_calling_agent: {e}")
    try:
        from langchain.agents import __all__ as agents_all
        print(f"Available in langchain.agents: {agents_all}")
    except Exception as ie:
        print(f"Failed to list langchain.agents: {ie}")
