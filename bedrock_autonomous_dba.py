
import asyncio
from mcp import StdioServerParameters

from InlineAgent.tools import MCPStdio
from InlineAgent.action_group import ActionGroup
from InlineAgent.agent import InlineAgent

# Step 1: Define MCP stdio parameters
postgres_dba_server_params = StdioServerParameters(
    command="python",
    args=["autonomous_dba_mcp.py"],
    env={
        "PGHOST": "localhost",
        "PGDATABASE": "autonomous_dba",
        "PGUSER": "dba_agent",
        "PGPASSWORD": "[PASSWORD]"
    }
)


async def main():
    # Step 2: Create MCP client
    postgres_client = await MCPStdio.create(server_params=postgres_dba_server_params)

    try:
        # Step 3: Define the action group with enhanced description
        dba_action_group = ActionGroup(
            name="PostgreSQLDBATools",
            description="Tools for autonomous PostgreSQL database management including slow query detection, query plan analysis, missing index identification, optimization knowledge search, and database statistics.",
            mcp_clients=[postgres_client],
        )

        # Step 4: Enhanced agent instructions with IDR framework
        agent_instruction = """You are an Autonomous PostgreSQL DBA agent for PostgreSQL Conference 2026 demo.

Your role is to help users identify, detect, and resolve database performance issues using the IDR (Identify → Detect → Resolve) framework.

## When a user asks to "find slow queries" or similar requests:

### IDENTIFY Phase:
1. Use get_slow_queries tool to retrieve slow-running queries from pg_stat_statements
2. Use get_missing_indexes tool to identify tables with high sequential scans
3. Use get_database_statistics tool to understand overall database health

### DETECT Phase:
1. For each slow query identified, use analyze_query_plan tool to get detailed execution plans
2. Look for bottlenecks such as:
   - Sequential scans on large tables
   - Missing indexes on join columns
   - Inefficient join strategies
   - Correlated subqueries
   - Full table scans on filtered queries

### RESOLVE Phase:
1. Use search_optimization_knowledge tool to find similar historical patterns and proven solutions
2. Generate specific, actionable recommendations such as:
   - CREATE INDEX statements with exact syntax
   - Query rewrite suggestions
   - Configuration parameter changes
3. Explain the expected performance improvement based on historical data

## Response Format:
Always structure your response as:
1. **Identified Issues**: List what slow queries or problems were found
2. **Root Cause Analysis**: Explain why these queries are slow (missing indexes, poor query structure, etc.)
3. **Recommendations**: Provide specific SQL commands to fix the issues
4. **Expected Impact**: Estimate the performance improvement based on knowledge base patterns

## Important Guidelines:
- Always explain your findings in clear, conference-presentation-friendly language
- Provide specific SQL commands that can be copy-pasted
- Reference the dba_knowledge_base patterns when making recommendations
- Be proactive - if you find issues, suggest fixes immediately
- Use technical accuracy suitable for a PostgreSQL conference audience"""

        # Step 5: Get user input and invoke the Bedrock Inline Agent
        user_input = input("Enter your request (e.g., 'find my slow queries'): ")
        
        print("Autonomous DBA Agent is analyzing your database..")
        
        await InlineAgent(
            foundation_model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            instruction=agent_instruction,
            agent_name="autonomous-postgresql-dba",
            action_groups=[dba_action_group],
        ).invoke(
            input_text=user_input
        )

    finally:
        await postgres_client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


