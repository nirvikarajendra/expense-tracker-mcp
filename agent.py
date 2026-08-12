from dotenv import load_dotenv
import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

load_dotenv()

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://expense-tracker-nirvika.fastmcp.app/mcp",
        headers={
            "Authorization": f"Bearer {os.getenv('MCP_API_KEY')}"
        }
        )
    )

root_agent = LlmAgent(
    name="expense_tracker_agent",
    model="gemini-3.5-flash",
    instruction="You are an expense management assistant. Use the available MCP tools when needed.",
    tools=[mcp_toolset]
)


