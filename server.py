from mcp.server.fastmcp import FastMCP
import httpx
import os

# Initialize FastMCP server
mcp = FastMCP("weeek-mcp")

# Base URL for Weeek API
BASE_URL = "https://api.weeek.net/public/v1"

def get_headers():
    api_key = os.environ.get("WEEEK_API_KEY")
    if not api_key:
        raise ValueError("WEEEK_API_KEY environment variable is not set")
    return {
        "Authorization": f"Bearer {api_key}"
    }

@mcp.tool()
async def get_workspaces() -> str:
    """Get a list of workspaces in Weeek."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workspace",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_projects() -> str:
    """Get a list of projects in Weeek."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tm/projects",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_tasks() -> str:
    """Get a list of tasks in Weeek."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tm/tasks",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def create_task(title: str, project_id: int = None) -> str:
    """Create a new task in Weeek."""
    payload = {"title": title}
    if project_id:
        payload["projectId"] = project_id
        
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tm/tasks",
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    mcp.run()
