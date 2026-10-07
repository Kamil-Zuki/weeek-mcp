# weeek-mcp

An MCP (Model Context Protocol) server for the [Weeek.net](https://weeek.net/) API.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API key:
   You can get your API key from your workspace settings in Weeek under the API section.

   ```bash
   # Windows PowerShell
   $env:WEEEK_API_KEY="your-api-key"
   ```

## Usage

Run the server:
```bash
python server.py
```

## Features

Provides tools to interact with Weeek:
- `get_workspaces`: List available workspaces.
- `get_users`: Get a list of users in the workspace.
- `get_projects`: List projects.
- `get_boards`: List boards.
- `get_tasks`: List tasks.
- `get_task`: Get details of a specific task.
- `create_task`: Create a new task.
- `update_task`: Update a specific task.
- `delete_task`: Delete a specific task.

You can add more tools by referring to the [Weeek API Documentation](https://developers.weeek.net/).
