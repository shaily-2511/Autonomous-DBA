import asyncio
import boto3
import psycopg2
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'database': 'autonomous_dba',
    'user': 'dba_agent',
    'password': 'PASSWORD',  # Update with your actual password
    'port': 5432
}

def format_bytes(bytes_value):
    """Helper function to format bytes into human-readable format"""
    if bytes_value is None:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

async def check_unused_indexes(conn):
    """Monitor unused and rarely used indexes"""
    try:
        cursor = conn.cursor()
        query = """
        SELECT
            schemaname,
            relname AS tablename,
            indexrelname AS indexname,
            idx_scan AS scans,
            pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
            pg_relation_size(indexrelid) AS index_size_bytes,
            0.0 AS pct_of_table,
            CASE
                WHEN idx_scan = 0 THEN 'NEVER_USED'
                WHEN idx_scan < 10 THEN 'RARELY_USED'
                WHEN idx_scan < 100 THEN 'LOW_USAGE'
                ELSE 'ACTIVE'
            END AS usage_category
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
          AND indexrelname NOT LIKE '%_pkey'
          AND indexrelname NOT LIKE '%_unique'
          AND idx_scan < 100
        ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        never_used = []
        rarely_used = []
        low_usage = []
        for row in results:
            index_info = {
                'schemaname': row[0],
                'tablename': row[1],
                'indexname': row[2],
                'scans': row[3],
                'index_size': row[4],
                'index_size_bytes': row[5],
                'pct_of_table': row[6],
                'usage_category': row[7]
            }
            if index_info['usage_category'] == 'NEVER_USED':
                never_used.append(index_info)
            elif index_info['usage_category'] == 'RARELY_USED':
                rarely_used.append(index_info)
            elif index_info['usage_category'] == 'LOW_USAGE':
                low_usage.append(index_info)
        cursor.close()
        total_wasted = sum(idx['index_size_bytes'] for idx in never_used)
        return {
            'never_used': never_used,
            'rarely_used': rarely_used,
            'low_usage': low_usage,
            'total_wasted_bytes': total_wasted
        }
    except Exception as e:
        return {'error': str(e)}



async def check_database_health():
    """Perform health checks on PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Check 1: Active connections
        cursor.execute("""
            SELECT count(*) as active_connections,
                   (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
            FROM pg_stat_activity
            WHERE state = 'active';
        """)
        active_conn, max_conn = cursor.fetchone()
        conn_percent = (active_conn / max_conn) * 100
        # Check 2: Table bloat
        cursor.execute("""
            SELECT schemaname, relname as tablename, n_dead_tup, n_live_tup,
                   ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_percent
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 0
            ORDER BY dead_tuple_percent DESC NULLS LAST
            LIMIT 5;
        """)
        bloat_results = cursor.fetchall()
        # Check 3: Unused indexes
        index_results = await check_unused_indexes(conn)
        cursor.close()
        conn.close()
        return {
            'timestamp': datetime.now().isoformat(),
            'connection_usage': f"{conn_percent:.1f}%",
            'active_connections': active_conn,
            'max_connections': max_conn,
            'bloat_detected': len(bloat_results) > 0,
            'bloat_tables': bloat_results,
            'index_analysis': index_results
        }
    except Exception as e:
        return {'error': str(e)}

async def continuous_monitoring():
    print("=" * 60)
    print("HEALTH CHECK AGENT - Autonomous DBA System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Role: Continuous Monitoring")
    print("- Monitors database health metrics")
    print("- Detects anomalies and issues")
    print("- Reports findings to Supervisor Agent")
    print("Monitoring Interval: 60 seconds")
    print("=" * 60)
    check_count = 0
    try:
        while True:
            check_count += 1
            print(f"[Check #{check_count}] {datetime.now().strftime('%H:%M:%S')}")
            health_status = await check_database_health()
            if 'error' in health_status:
                print(f"❌ Error: {health_status['error']}")
            else:
                print(f"✓ Connection Usage: {health_status['connection_usage']}")
                print(f"✓ Active Connections: {health_status['active_connections']}/{health_status['max_connections']}")
                if health_status['bloat_detected']:
                    print(f"⚠️  Table Bloat Detected:")
                    for table in health_status['bloat_tables']:
                        schema, tablename, dead_tup, live_tup, dead_percent = table
                        print(f"   - {schema}.{tablename}: {dead_percent}% dead tuples")
                        if dead_percent > 20:
                            print(f"     🔴 ALERT: Requires VACUUM")
                            print(f"     💡 Recommendation: VACUUM ANALYZE {tablename};")
                else:
                    print("✓ No significant table bloat detected")
                if 'index_analysis' in health_status and 'error' not in health_status['index_analysis']:
                    index_data = health_status['index_analysis']
                    if index_data['never_used']:
                        print(f"⚠️  UNUSED INDEXES DETECTED: {len(index_data['never_used'])} indexes")
                        print(f"   Total wasted space: {format_bytes(index_data['total_wasted_bytes'])}")
                        print(f"   Details:")
                        for idx in index_data['never_used']:
                            print(f"   • {idx['indexname']}")
                            print(f"     Table: {idx['tablename']}")
                            print(f"     Size: {idx['index_size']}")
                            print(f"     Scans: {idx['scans']} (never used)")
                            print(f"     % of table: {idx['pct_of_table']}%")
                            print(f"     DROP Query: DROP INDEX IF EXISTS {idx['schemaname']}.{idx['indexname']};")
                    if index_data['rarely_used']:
                        print(f"🟡 RARELY USED INDEXES: {len(index_data['rarely_used'])} indexes")
                        for idx in index_data['rarely_used']:
                            print(f"   • {idx['indexname']}: {idx['scans']} scans")
                    if index_data['low_usage']:
                        print(f"🟢 LOW USAGE INDEXES: {len(index_data['low_usage'])} indexes (monitoring)")
                    if not index_data['never_used'] and not index_data['rarely_used'] and not index_data['low_usage']:
                        print("✓ All indexes are actively used")
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("Health Check Agent shutting down...")

if __name__ == "__main__":
    asyncio.run(continuous_monitoring())

