from mcp.server.mcpserver import MCPServer
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize MCPServer
mcp = MCPServer("weeek-mcp")

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
async def get_tasks(project_id: int = None, board_id: int = None) -> str:
    """Get a list of tasks in Weeek. Can be filtered by project_id or board_id."""
    params = {}
    if project_id:
        params["projectId"] = project_id
    if board_id:
        params["boardId"] = board_id
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tm/tasks",
            headers=get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def create_task(
    title: str, 
    description: str = None, 
    project_id: int = None, 
    board_id: int = None, 
    board_column_id: int = None
) -> str:
    """Create a new task in Weeek. Can optionally specify description, project, board, and column."""
    payload = {"title": title}
    if description:
        payload["description"] = description
    if project_id:
        payload["projectId"] = project_id
    if board_id:
        payload["boardId"] = board_id
    if board_column_id:
        # Note: Weeek API might use 'boardColumnId' or 'columnId'. 
        payload["boardColumnId"] = board_column_id
        
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tm/tasks",
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_task(task_id: int) -> str:
    """Get details of a specific task."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tm/tasks/{task_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def update_task(task_id: int, title: str = None, description: str = None) -> str:
    """Update a specific task."""
    payload = {}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
        
    async with httpx.AsyncClient() as client:
        # Many APIs use POST, PATCH or PUT for updates. Usually Weeek uses PUT or PATCH. We'll use PUT/PATCH
        response = await client.put(
            f"{BASE_URL}/tm/tasks/{task_id}",
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def delete_task(task_id: int) -> str:
    """Delete a specific task."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/tm/tasks/{task_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return "Task deleted successfully"

@mcp.tool()
async def get_boards(project_id: int = None) -> str:
    """Get a list of boards in Weeek. Can be filtered by project_id."""
    params = {}
    if project_id:
        params["projectId"] = project_id
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tm/boards",
            headers=get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_users() -> str:
    """Get a list of users in the workspace."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/workspace/users",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.text

if __name__ == "__main__":
    mcp.run()
