"""
Database management for E-commerce Price Tracker
Handles SQLite operations with proper indexing for performance
"""
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def init_db(db_path="tracker.db"):
    """
    Initialize the database with proper schema and indexes
    
    Args:
        db_path: Path to SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create prices table with aligned schema
        c.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                name TEXT,
                price TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add indexes for performance optimization
        c.execute('CREATE INDEX IF NOT EXISTS idx_product ON prices(product)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON prices(timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_product_timestamp ON prices(product, timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"[DATABASE] Initialized database at {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"[DATABASE] Error initializing database: {e}")
        return False


def insert_price(product, name, price, db_path="tracker.db"):
    """
    Insert a price record into the database
    
    Args:
        product: Product search query/identifier
        name: Product name
        price: Product price
        db_path: Path to SQLite database file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO prices (product, name, price, timestamp) VALUES (?, ?, ?, ?)",
            (product, name, price, datetime.now())
        )
        
        conn.commit()
        conn.close()
        
        logger.debug(f"[DATABASE] Inserted price for {product}: {name} - {price}")
        return True
        
    except Exception as e:
        logger.error(f"[DATABASE] Error inserting price: {e}")
        return False


def get_price_history(product, db_path="tracker.db", limit=None):
    """
    Get price history for a product
    
    Args:
        product: Product identifier
        db_path: Path to SQLite database file
        limit: Maximum number of records to return (None for all)
    
    Returns:
        List of price records
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        query = """
            SELECT name, price, timestamp 
            FROM prices 
            WHERE product = ? 
            ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        c.execute(query, (product,))
        rows = c.fetchall()
        conn.close()
        
        return [
            {"name": r[0], "price": r[1], "timestamp": r[2]}
            for r in rows
        ]
        
    except Exception as e:
        logger.error(f"[DATABASE] Error fetching price history: {e}")
        return []


def get_latest_prices(db_path="tracker.db", limit=10):
    """
    Get latest tracked prices across all products
    
    Args:
        db_path: Path to SQLite database file
        limit: Maximum number of records to return
    
    Returns:
        List of latest price records
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT product, name, price, timestamp 
            FROM prices 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        return [
            {"product": r[0], "name": r[1], "price": r[2], "timestamp": r[3]}
            for r in rows
        ]
        
    except Exception as e:
        logger.error(f"[DATABASE] Error fetching latest prices: {e}")
        return []
