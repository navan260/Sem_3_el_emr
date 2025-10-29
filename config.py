"""
Database Configuration
======================
Centralized database configuration supporting both local and cloud (Railway) MySQL
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
# This is crucial so os.getenv() can find the variables
load_dotenv()

# =============================================================================
# LOCAL DATABASE CONFIGURATION (for development)
# =============================================================================
# This block now reads from your .env file when USE_RAILWAY=false
LOCAL_DB_CONFIG: Dict[str, any] = {
    'host': os.getenv('LOCAL_MYSQL_HOST', '127.0.0.1'),
    'port': int(os.getenv('LOCAL_MYSQL_PORT', 3306)),
    'user': os.getenv('LOCAL_MYSQL_USER', 'root'),
    'password': os.getenv('LOCAL_MYSQL_PASSWORD', ''), # Reads from .env
    'database': os.getenv('LOCAL_MYSQL_DATABASE', 'clinic'), # Reads from .env
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# =============================================================================
# RAILWAY (CLOUD) DATABASE CONFIGURATION
# =============================================================================
# Railway provides these as environment variables
# Get them from Railway dashboard -> Your Project -> Variables
RAILWAY_DB_CONFIG: Dict[str, any] = {
    'host': os.getenv('MYSQL_HOST', 'yamanote.proxy.rlwy.net'),
    'port': int(os.getenv('MYSQL_PORT', 36350)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'your_railway_password'),
    'database': os.getenv('MYSQL_DATABASE', 'railway'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# =============================================================================
# ACTIVE CONFIGURATION
# =============================================================================
# Set USE_RAILWAY = True to use Railway cloud database
# Set USE_RAILWAY = False to use local MySQL
USE_RAILWAY = os.getenv('USE_RAILWAY', 'False').lower() == 'true'

# Select active configuration
if USE_RAILWAY:
    DB_CONFIG = RAILWAY_DB_CONFIG
    print("🌐 Using Railway Cloud Database")
else:
    DB_CONFIG = LOCAL_DB_CONFIG
    print("💻 Using Local/Custom MySQL Database") # Renamed for clarity


# =============================================================================
# HELPER FUNCTION TO GET DATABASE URL
# =============================================================================
def get_database_url() -> str:
    """
    Generate database connection URL

    Returns:
        MySQL connection URL string
    """
    config = DB_CONFIG
    # Handle empty password
    password = f":{config['password']}" if config['password'] else ""
    return f"mysql://{config['user']}{password}@{config['host']}:{config['port']}/{config['database']}"


def print_config():
    """Print current database configuration (without password)"""
    config = DB_CONFIG.copy()
    config['password'] = '****' + config['password'][-4:] if config['password'] else '****'

    print("=" * 60)
    print("DATABASE CONFIGURATION")
    print("=" * 60)
    for key, value in config.items():
        print(f"{key:15}: {value}")
    print("=" * 60)


if __name__ == "__main__":
    print_config()
