import os
import json
from typing import Optional, List, Dict, Any, Union
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("weeek-mcp")

BASE_URL = "https://api.weeek.net/public/v1"

def get_headers() -> Dict[str, str]:
    api_key = os.environ.get("WEEEK_API_KEY")
    if not api_key:
        raise ValueError("WEEEK_API_KEY environment variable is not set. Please set it in .env or environment.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

async def make_request(
    method: str, 
    endpoint: str, 
    params: Optional[Dict[str, Any]] = None, 
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper to execute requests with proper error handling."""
    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=get_headers(),
                params=params,
                json=json_data
            )
            response.raise_for_status()
            if response.status_code == 204 or not response.text.strip():
                return {"success": True}
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": e.response.text
            }
        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }

@mcp.tool()
async def get_projects() -> Dict[str, Any]:
    """Get a list of all projects in Weeek."""
    return await make_request("GET", "/tm/projects")

@mcp.tool()
async def get_boards(project_id: Optional[int] = None) -> Dict[str, Any]:
    """Get a list of boards in Weeek. Can be filtered by project_id."""
    params = {}
    if project_id is not None:
        params["projectId"] = project_id
    return await make_request("GET", "/tm/boards", params=params)

@mcp.tool()
async def get_tasks(
    project_id: Optional[int] = None,
    board_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 50,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a paginated list of tasks in Weeek.
    
    Args:
        project_id: Optional ID of the project to filter tasks.
        board_id: Optional ID of the board to filter tasks.
        page: Page number (starts at 1, default 1).
        per_page: Number of tasks per page (default 50, max 100).
        search: Optional search keyword to filter tasks by title/content.
    """
    params: Dict[str, Any] = {
        "page": page,
        "perPage": min(per_page, 100)
    }
    if project_id is not None:
        params["projectId"] = project_id
    if board_id is not None:
        params["boardId"] = board_id
    if search:
        params["search"] = search
        
    return await make_request("GET", "/tm/tasks", params=params)

@mcp.tool()
async def search_all_tasks(
    query: str,
    project_id: Optional[int] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Deep search for tasks by text across multiple pages or projects.
    
    Args:
        query: String or words to search for in task title or description.
        project_id: Optional project ID to limit the search.
        max_results: Maximum matching tasks to return (default 50).
    """
    query_lower = query.lower()
    matches = []
    page = 1
    
    while len(matches) < max_results:
        params: Dict[str, Any] = {
            "page": page,
            "perPage": 50,
            "search": query
        }
        if project_id is not None:
            params["projectId"] = project_id
            
        data = await make_request("GET", "/tm/tasks", params=params)
        if data.get("error"):
            return data
            
        tasks = data.get("tasks", data.get("data", []))
        if not tasks:
            break
            
        for t in tasks:
            t_title = str(t.get("title", "")).lower()
            t_desc = str(t.get("description", "")).lower()
            if query_lower in t_title or query_lower in t_desc:
                matches.append(t)
                if len(matches) >= max_results:
                    break
                    
        has_more = data.get("hasMore", False)
        if not has_more or len(tasks) < 50:
            break
        page += 1

    return {
        "query": query,
        "count": len(matches),
        "tasks": matches
    }

@mcp.tool()
async def get_task(task_id: int) -> Dict[str, Any]:
    """Get full details of a specific task by its ID."""
    return await make_request("GET", f"/tm/tasks/{task_id}")

@mcp.tool()
async def create_task(
    title: str, 
    description: Optional[str] = None, 
    project_id: Optional[int] = None, 
    board_id: Optional[int] = None, 
    board_column_id: Optional[int] = None,
    priority: Optional[int] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task in Weeek.
    
    Args:
        title: Title of the task.
        description: Task description (supports HTML/markdown).
        project_id: Project ID.
        board_id: Board ID.
        board_column_id: Column ID on the board.
        priority: Priority level (e.g. 1 - Low, 2 - Medium, 3 - High).
        due_date: Due date formatted as YYYY-MM-DD.
    """
    payload: Dict[str, Any] = {"title": title}
    if description:
        payload["description"] = description
    if project_id is not None:
        payload["projectId"] = project_id
    if board_id is not None:
        payload["boardId"] = board_id
    if board_column_id is not None:
        payload["boardColumnId"] = board_column_id
    if priority is not None:
        payload["priority"] = priority
    if due_date:
        payload["dueDate"] = due_date
        
    return await make_request("POST", "/tm/tasks", json_data=payload)

@mcp.tool()
async def update_task(
    task_id: int, 
    title: Optional[str] = None, 
    description: Optional[str] = None,
    is_completed: Optional[bool] = None,
    priority: Optional[int] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task in Weeek.
    
    Args:
        task_id: ID of the task to update.
        title: New title.
        description: New description.
        is_completed: Set task completion status (True/False).
        priority: Priority level.
        due_date: Due date (YYYY-MM-DD).
    """
    payload: Dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if is_completed is not None:
        payload["isCompleted"] = is_completed
    if priority is not None:
        payload["priority"] = priority
    if due_date is not None:
        payload["dueDate"] = due_date
        
    return await make_request("PUT", f"/tm/tasks/{task_id}", json_data=payload)

@mcp.tool()
async def delete_task(task_id: int) -> Dict[str, Any]:
    """Delete a task by ID."""
    return await make_request("DELETE", f"/tm/tasks/{task_id}")

@mcp.tool()
async def get_users() -> Dict[str, Any]:
    """Get a list of users in the workspace."""
    return await make_request("GET", "/workspace/users")

if __name__ == "__main__":
    mcp.run()
