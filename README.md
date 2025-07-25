### End to End Project Agentic AI Chatbot using Langgraph

# AgenticChatbot: Tools Module

This directory contains utility modules to integrate external tools (such as web search) into your LangGraph agentic chatbot pipeline.

## Contents

- `search_tool.py`: Functions to instantiate and wrap search tools for use with LangGraph.
- `__init__.py`: Marks this directory as a Python package.

## Functionality

### `search_tool.py`

Provides the following utilities:

- **get_tool()**  
  Returns a list of tools to be used by the chatbot. Currently, it includes the `TavilySearchResults` tool, which enables the agent to perform web searches and retrieve up to 2 results.

- **create_tool_node(tools)**  
  Takes a list of tools and returns a `ToolNode`—a LangGraph node configured with those tools. This allows seamless integration of external capabilities (like web search) into the chatbot’s multi-agent workflow.

### Dependencies

- [LangChain Community Tools](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)

Ensure you have these libraries installed in your environment.

## Usage Example

```python
from langgraphagenticai.tools.search_tool import get_tool, create_tool_node

# Initialize tools
tools = get_tool()

# Create a ToolNode for LangGraph workflows
tool_node = create_tool_node(tools)
