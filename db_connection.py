"""
Database Connection Module
===========================
MySQL database connection handler for clinic management system
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Tuple
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("✅ Connected to MySQL Server")
            return connection
    except Error as e:
        logger.error(f"❌ Error connecting to MySQL: {e}")
        return None


def close_connection(connection):
    """Close database connection"""
    if connection and connection.is_connected():
        connection.close()
        logger.info("✅ Database connection closed")


def test_connection():
    """Test database connection"""
    connection = create_connection()
    if connection:
        close_connection(connection)
        return True
    return False


def execute_query(connection, query: str, params: Tuple = None) -> bool:
    """Execute INSERT, UPDATE, DELETE queries"""
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        logger.info(f"✅ Query executed. Rows affected: {cursor.rowcount}")
        cursor.close()
        return True
    except Error as e:
        logger.error(f"❌ Error executing query: {e}")
        return False


def execute_select_query(connection, query: str, params: Tuple = None) -> List[Dict]:
    """Execute SELECT queries"""
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        logger.info(f"✅ Query executed. Rows returned: {len(results)}")
        return results
    except Error as e:
        logger.error(f"❌ Error executing SELECT query: {e}")
        return []


def execute_insert_query(connection, query: str, params: Tuple) -> Optional[int]:
    """Execute INSERT query and return last inserted ID"""
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        logger.info(f"✅ Insert successful. Last ID: {last_id}")
        return last_id
    except Error as e:
        logger.error(f"❌ Error executing INSERT query: {e}")
        return None


def get_all_tables(connection) -> List[str]:
    """Get list of all tables"""
    query = "SHOW TABLES"
    results = execute_select_query(connection, query)
    return [list(row.values())[0] for row in results]


def run_diagnostics():
    """Run database diagnostics"""
    print("\n" + "=" * 60)
    print("DATABASE DIAGNOSTICS")
    print("=" * 60)

    connection = create_connection()
    if not connection:
        print("❌ Connection failed!")
        return

    print("\n1. Getting all tables...")
    tables = get_all_tables(connection)
    print(f"   Tables found: {', '.join(tables)}")

    print("\n2. Record counts:")
    for table in tables:
        query = f"SELECT COUNT(*) as count FROM {table}"
        result = execute_select_query(connection, query)
        count = result[0]['count'] if result else 0
        print(f"   {table}: {count} records")

    close_connection(connection)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if test_connection():
        print("\n✅ Connection test passed!\n")
        run_diagnostics()
    else:
        print("\n❌ Connection test failed!")
