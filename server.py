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
    user_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a paginated list of tasks in Weeek.
    
    Args:
        project_id: Optional ID of the project to filter tasks.
        board_id: Optional ID of the board to filter tasks.
        user_id: Optional ID of the assigned user/member.
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
    if user_id:
        params["userId"] = user_id
    if search:
        params["search"] = search
        
    return await make_request("GET", "/tm/tasks", params=params)

@mcp.tool()
async def get_tasks_by_assignee(
    user_query: str,
    project_id: Optional[int] = None,
    is_completed: Optional[bool] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Find tasks assigned to a specific person by their name, surname, email, or user ID.
    
    Args:
        user_query: Name, surname, email or UUID of the person (e.g. 'Радченко', 'Zuko', 'alex@mail.com').
        project_id: Optional project ID to limit search.
        is_completed: Filter by completion status (True for completed, False for in-progress, None for all).
        max_results: Maximum tasks to return (default 50).
    """
    # 1. Resolve member from workspace
    members_data = await make_request("GET", "/ws/members")
    if members_data.get("error"):
        return members_data
        
    members = members_data.get("members", [])
    query_norm = user_query.strip().lower()
    
    matched_members = []
    for m in members:
        uid = str(m.get("id", "")).lower()
        first_name = str(m.get("firstName", "")).lower()
        last_name = str(m.get("lastName", "")).lower()
        email = str(m.get("email", "")).lower()
        full_name = f"{first_name} {last_name}".strip()
        
        if (query_norm == uid or 
            query_norm in first_name or 
            query_norm in last_name or 
            query_norm in full_name or 
            query_norm in email):
            matched_members.append(m)
            
    if not matched_members:
        return {
            "error": False,
            "message": f"Пользователь '{user_query}' не найден среди участников воркспейса.",
            "available_members": [
                f"{m.get('firstName', '')} {m.get('lastName', '')} ({m.get('email', '')}) [id: {m.get('id')}]".strip()
                for m in members[:15]
            ],
            "count": 0,
            "tasks": []
        }
        
    target_user = matched_members[0]
    target_id = target_user.get("id")
    target_name = f"{target_user.get('firstName', '')} {target_user.get('lastName', '')}".strip() or target_user.get("email")

    # 2. Fetch tasks for this user
    matches = []
    offset = 0
    limit = 50
    
    while len(matches) < max_results:
        params: Dict[str, Any] = {
            "userId": target_id,
            "offset": offset,
            "perPage": limit
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
            if is_completed is not None and t.get("isCompleted") != is_completed:
                continue
            matches.append(t)
            if len(matches) >= max_results:
                break
                
        has_more = data.get("hasMore", False)
        if not has_more or len(tasks) < limit:
            break
        offset += limit

    return {
        "user": {
            "id": target_id,
            "name": target_name,
            "email": target_user.get("email")
        },
        "count": len(matches),
        "tasks": matches
    }

@mcp.tool()
async def get_users() -> Dict[str, Any]:
    """Get a list of users/members in the workspace."""
    return await make_request("GET", "/ws/members")

@mcp.tool()
async def search_all_tasks(
    query: str,
    project_id: Optional[int] = None,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Deep search for tasks by text across multiple pages or projects.
    Supports multi-word queries: matches tasks that contain all specified words.
    
    Args:
        query: Search query (can be multiple words like 'Henderson МПК').
        project_id: Optional project ID to limit the search.
        max_results: Maximum matching tasks to return (default 50).
    """
    words = [w.strip().lower() for w in query.split() if w.strip()]
    if not words:
        return {"query": query, "count": 0, "tasks": []}

    matches = []
    seen_ids = set()
    offset = 0
    limit = 50
    
    # Use the longest word for Weeek API server-side search filter
    primary_keyword = max(words, key=len)
    
    while len(matches) < max_results:
        params: Dict[str, Any] = {
            "offset": offset,
            "perPage": limit,
            "search": primary_keyword
        }
        if project_id is not None:
            params["projectId"] = project_id
            
        data = await make_request("GET", "/tm/tasks", params=params)
        if data.get("error"):
            return data
            
        tasks = data.get("tasks", data.get("data", []))
        if not tasks:
            break
            
        new_tasks_added = 0
        for t in tasks:
            tid = t.get("id")
            if tid in seen_ids:
                continue
            seen_ids.add(tid)
            new_tasks_added += 1

            t_title = str(t.get("title", "")).lower()
            t_desc = str(t.get("description", "")).lower()
            full_text = f"{t_title} {t_desc}"
            
            # Check that ALL words from query are present in title or description
            if all(w in full_text for w in words):
                matches.append(t)
                if len(matches) >= max_results:
                    break
                    
        has_more = data.get("hasMore", False)
        if not has_more or new_tasks_added == 0:
            break
            
        offset += limit

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

if __name__ == "__main__":
    mcp.run()
