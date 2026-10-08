# weeek-mcp

An MCP (Model Context Protocol) server for the [Weeek.net](https://weeek.net/) API. Connects LLM clients (such as Claude Desktop, Cursor, Gemini IDE) directly to your Weeek workspace.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   Create a `.env` file or export your API key:
   ```env
   WEEEK_API_KEY="your-api-key"
   ```

3. **Add to MCP Configuration** (e.g. `mcp_config.json` / Claude Desktop config):
   ```json
   {
     "mcpServers": {
       "weeek": {
         "command": "python",
         "args": [
           "path/to/weeek-mcp/server.py"
         ],
         "env": {
           "WEEEK_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

## Features & Tools

- **`search_all_tasks(query, project_id, max_results)`**: Deep text search across tasks, titles, and descriptions.
- **`get_tasks(project_id, board_id, page, per_page, search)`**: Get paginated list of tasks with optional board/project/search filters.
- **`get_task(task_id)`**: Retrieve full details of a specific task.
- **`create_task(title, description, project_id, board_id, board_column_id, priority, due_date)`**: Create a task with customizable parameters.
- **`update_task(task_id, title, description, is_completed, priority, due_date)`**: Update task fields or change completion status.
- **`delete_task(task_id)`**: Delete a task by ID.
- **`get_projects()`**: List all projects in the workspace.
- **`get_boards(project_id)`**: List boards in the workspace or specific project.
- **`get_users()`**: List workspace team members.

## License
MIT
