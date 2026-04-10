from mcp import StdioServerParameters

# PostgreSQL Autonomous DBA MCP Server parameters
postgres_dba_server_params = StdioServerParameters(
    command="python",
    args=["autonomous_dba_mcp.py"],
    env={
        "PGHOST": "localhost",
        "PGDATABASE": "autonomous_dba",
        "PGUSER": "dba_agent",
        "PGPASSWORD": "[PASSWORD]!"
    }
)
