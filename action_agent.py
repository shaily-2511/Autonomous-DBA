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
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

async def execute_vacuum(schema, table):
    """Execute VACUUM ANALYZE on specified table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(0)  # Autocommit mode
        cursor = conn.cursor()

        vacuum_query = f"VACUUM ANALYZE {schema}.{table};"
        print(f"   Executing: {vacuum_query}")

        start_time = datetime.now()
        cursor.execute(vacuum_query)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Verify bloat reduction
        cursor.execute(f"""
            SELECT
                n_live_tup,
                n_dead_tup,
                ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
            FROM pg_stat_user_tables
            WHERE schemaname = '{schema}' AND relname = '{table}';
        """)
        result = cursor.fetchone()

        if result:
            live_tup, dead_tup, dead_pct = result
            print(f"   ✓ VACUUM completed in {duration:.2f} seconds")
            print(f"   ✓ Bloat reduced to {dead_pct}%")
            print(f"   ✓ Live tuples: {live_tup:,}, Dead tuples: {dead_tup:,}")

        cursor.close()
        conn.close()

        return {
            'status': 'success',
            'action': f'VACUUM ANALYZE {schema}.{table}',
            'duration': duration,
            'after_bloat': dead_pct if result else None
        }

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {'status': 'error', 'error': str(e)}

async def drop_unused_indexes(indexes):
    """Drop unused indexes to free space"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(0)  # Autocommit mode
        cursor = conn.cursor()

        print(f"🔧 Remediating unused indexes: {len(indexes)} indexes to drop")

        dropped_indexes = []
        total_space_freed = 0

        for idx in indexes:
            schema = idx['schemaname']
            indexname = idx['indexname']
            tablename = idx['tablename']
            size_bytes = idx['index_size_bytes']

            try:
                drop_query = f"DROP INDEX IF EXISTS {schema}.{indexname};"
                print(f"   Executing: {drop_query}")

                start_time = datetime.now()
                cursor.execute(drop_query)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                print(f"   ✓ Dropped {indexname} from {tablename} ({format_bytes(size_bytes)}) in {duration:.2f}s")

                dropped_indexes.append({
                    'index': indexname,
                    'table': tablename,
                    'size': format_bytes(size_bytes),
                    'duration': duration
                })
                total_space_freed += size_bytes

            except Exception as e:
                print(f"   ✗ Error dropping {indexname}: {e}")

        cursor.close()
        conn.close()

        print(f"   ✓ Total space freed: {format_bytes(total_space_freed)}")
        print(f"   ✓ Successfully dropped {len(dropped_indexes)} indexes")

        return {
            'status': 'success',
            'action': 'DROP UNUSED INDEXES',
            'dropped_count': len(dropped_indexes),
            'total_space_freed': format_bytes(total_space_freed),
            'dropped_indexes': dropped_indexes
        }

    except Exception as e:
        print(f"   ✗ Error during index remediation: {e}")
        return {'status': 'error', 'error': str(e)}

async def main():
    print("=" * 60)
    print("ACTION AGENT - Autonomous DBA System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Role: Remediation and Optimization")
    print("- Executes corrective actions")
    print("- Performs VACUUM and ANALYZE operations")
    print("- Drops unused indexes to free space")
    print("- Creates indexes and optimizes queries")
    print("Status: READY (Waiting for remediation requests)")
    print("=" * 60)

    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("Action Agent shutting down...")

if __name__ == "__main__":
    asyncio.run(main())


