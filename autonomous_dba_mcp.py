from mcp.server.fastmcp import FastMCP
import psycopg2
import json

# Initialize MCP server
app = FastMCP("autonomous-dba")

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="autonomous_dba",
        user="dba_agent",
        password="[PASSWORD]!"
    )

# Tool 1: Get slow queries from pg_stat_statements
@app.tool()
async def get_slow_queries(min_execution_time_ms: int = 1000, limit: int = 10) -> str:
    """
    Identifies slow-running queries from pg_stat_statements extension.
    Returns queries with execution time, calls, and query text.
    
    Args:
        min_execution_time_ms: Minimum average execution time in milliseconds to consider a query slow (default: 1000ms)
        limit: Maximum number of slow queries to return (default: 10)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                queryid,
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > %s
            ORDER BY mean_exec_time DESC
            LIMIT %s;
        """, (min_execution_time_ms, limit))
        
        results = cur.fetchall()
        slow_queries = []
        
        for row in results:
            slow_queries.append({
                "query_id": str(row[0]),
                "query": row[1],
                "calls": row[2],
                "total_time_ms": round(float(row[3]), 2),
                "avg_time_ms": round(float(row[4]), 2),
                "max_time_ms": round(float(row[5]), 2),
                "rows": row[6]
            })
        
        return json.dumps({
            "status": "success",
            "count": len(slow_queries),
            "slow_queries": slow_queries
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        conn.close()

# Tool 2: Analyze query execution plan
@app.tool()
async def analyze_query_plan(query: str) -> str:
    """
    Runs EXPLAIN ANALYZE on a specific query to get detailed execution plan 
    and identify bottlenecks like sequential scans, missing indexes, or inefficient joins.
    
    Args:
        query: SQL query to analyze
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Use EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for detailed analysis
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
        plan = cur.fetchone()[0]
        
        return json.dumps({
            "status": "success",
            "query": query,
            "execution_plan": plan
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e), "query": query})
    finally:
        conn.close()

# Tool 3: Search optimization knowledge base
@app.tool()
async def search_optimization_knowledge(query_pattern: str, top_k: int = 3) -> str:
    """
    Searches the dba_knowledge_base to find relevant optimization strategies 
    for a given query pattern or performance issue.
    
    Args:
        query_pattern: Description of the query pattern or performance issue
        top_k: Number of similar patterns to retrieve (default: 3)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Text-based search (can be enhanced with vector similarity later)
        cur.execute("""
            SELECT 
                query_pattern,
                optimization_strategy,
                query_type,
                complexity_level,
                estimated_improvement,
                metadata
            FROM dba_knowledge_base
            WHERE query_pattern ILIKE %s
            ORDER BY id
            LIMIT %s;
        """, (f"%{query_pattern}%", top_k))
        
        results = cur.fetchall()
        knowledge = []
        
        for row in results:
            knowledge.append({
                "pattern": row[0],
                "strategy": row[1],
                "type": row[2],
                "complexity": row[3],
                "improvement": row[4],
                "metadata": row[5]
            })
        
        return json.dumps({
            "status": "success",
            "query_pattern": query_pattern,
            "matches_found": len(knowledge),
            "recommendations": knowledge
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        conn.close()

# Tool 4: Get missing indexes
@app.tool()
async def get_missing_indexes(min_seq_scans: int = 1000) -> str:
    """
    Identifies tables with missing indexes based on sequential scans and table sizes.
    Tables with high sequential scan counts and large row counts are candidates for indexing.
    
    Args:
        min_seq_scans: Minimum number of sequential scans to flag (default: 1000)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                seq_scan,
                seq_tup_read,
                idx_scan,
                n_live_tup,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
            FROM pg_stat_user_tables
            WHERE seq_scan > %s
            AND n_live_tup > 10000
            ORDER BY seq_scan DESC
            LIMIT 10;
        """, (min_seq_scans,))
        
        results = cur.fetchall()
        tables = []
        
        for row in results:
            tables.append({
                "schema": row[0],
                "table": row[1],
                "seq_scans": row[2],
                "rows_scanned": row[3],
                "index_scans": row[4] if row[4] else 0,
                "live_rows": row[5],
                "table_size": row[6]
            })
        
        return json.dumps({
            "status": "success",
            "tables_needing_indexes": len(tables),
            "tables": tables
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        conn.close()

# Tool 5: Get active queries
@app.tool()
async def get_active_queries() -> str:
    """
    Retrieve currently running queries from pg_stat_activity.
    Useful for identifying long-running queries in real-time.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                pid, 
                usename, 
                state, 
                query, 
                query_start,
                now() - query_start AS duration
            FROM pg_stat_activity
            WHERE state = 'active'
            AND query NOT LIKE '%pg_stat_activity%'
            ORDER BY duration DESC;
        """)
        results = cur.fetchall()
        
        active_queries = []
        for row in results:
            active_queries.append({
                "pid": row[0],
                "user": row[1],
                "state": row[2],
                "query": row[3],
                "query_start": str(row[4]),
                "duration": str(row[5])
            })
        
        return json.dumps({
            "status": "success",
            "active_queries_count": len(active_queries),
            "queries": active_queries
        }, default=str, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        conn.close()

# Tool 6: Get database statistics
@app.tool()
async def get_database_statistics() -> str:
    """
    Retrieve overall database statistics including table sizes, row counts, 
    and index usage to provide context for optimization recommendations.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                n_live_tup as row_count,
                seq_scan,
                idx_scan
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 20;
        """)
        
        results = cur.fetchall()
        tables = []
        
        for row in results:
            tables.append({
                "schema": row[0],
                "table": row[1],
                "size": row[2],
                "row_count": row[3],
                "seq_scans": row[4],
                "index_scans": row[5] if row[5] else 0
            })
        
        return json.dumps({
            "status": "success",
            "database": "autonomous_dba",
            "tables": tables
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run()
