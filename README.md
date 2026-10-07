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
- `get_projects`: List projects.
- `get_tasks`: List tasks.
- `create_task`: Create a new task.

You can add more tools by referring to the [Weeek API Documentation](https://developers.weeek.net/).
