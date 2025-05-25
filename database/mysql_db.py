# database/mysql_db.py

import mysql.connector
from mysql.connector import Error
from config import config
from datetime import datetime

def create_mysql_connection():
    """Create a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(**config.MYSQL_CONFIG)
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            setup_mysql_schema(connection)
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def setup_mysql_schema(connection):
    """Set up the MySQL database schema"""
    try:
        cursor = connection.cursor()
        
        # Drop existing tables to ensure clean schema
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS messages")
        
        # Create messages table with matching schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_jid VARCHAR(255),
            sender VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME,
            is_from_me TINYINT(1),
            media_type VARCHAR(50),
            processed TINYINT(1) DEFAULT 0,
            bot_response TEXT
        )
        """)
        
        # Create transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            sender VARCHAR(255),
            action VARCHAR(50),
            brand VARCHAR(255),
            product VARCHAR(255),
            model VARCHAR(255),
            storage VARCHAR(50),
            color VARCHAR(50),
            quantity INT,
            price_amount DECIMAL(10,2),
            price_currency VARCHAR(10),
            price_per_unit TINYINT(1),
            region_market VARCHAR(255),
            region_warranty VARCHAR(255),
            `condition` VARCHAR(50),
            warranty VARCHAR(255),
            additional_details TEXT
        )
        """)
        
        connection.commit()
        cursor.close()
        print("MySQL schema initialized")
    except Error as e:
        print(f"Error setting up MySQL schema: {e}")

def store_message(connection, timestamp, sender, content, bot_response, chat_jid):
    """Store the user message and bot response in the MySQL database"""
    try:
        cursor = connection.cursor()
        
        # Debug: Print the exact values being passed
        print("\nDebug - Values being inserted:")
        print(f"timestamp: {timestamp} (type: {type(timestamp)})")
        print(f"sender: {sender} (type: {type(sender)})")
        print(f"content: {content[:100]}... (type: {type(content)})")
        print(f"bot_response: {bot_response[:100] if bot_response else None} (type: {type(bot_response)})")
        print(f"chat_jid: {chat_jid} (type: {type(chat_jid)})")
        
        # Convert timestamp to MySQL datetime format
        try:
            # First try parsing as datetime
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"Error parsing timestamp: {e}")
            # If parsing fails, use current time
            formatted_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\nFormatted timestamp: {formatted_timestamp}")
        
        # Try the insert with explicit type casting
        query = """
        INSERT INTO messages 
        (timestamp, sender, content, bot_response, chat_jid, processed, is_from_me, media_type)
        VALUES 
        (CAST(%s AS DATETIME), %s, %s, %s, %s, 1, 0, 'text')
        """
        values = (formatted_timestamp, sender, content, bot_response, chat_jid)
        
        print("\nDebug - Executing query:")
        print(f"Query: {query}")
        print(f"Values: {values}")
        
        try:
            cursor.execute(query, values)
            connection.commit()
            print("Message stored successfully")
        except Error as e:
            print(f"\nError executing query: {e}")
            print(f"Error code: {e.errno}")
            print(f"SQL state: {e.sqlstate}")
            print(f"Error message: {e.msg}")
            
            # Try alternative approach with prepared statement
            print("\nTrying alternative approach...")
            alt_query = """
            INSERT INTO messages 
            (timestamp, sender, content, bot_response, chat_jid, processed, is_from_me, media_type)
            VALUES 
            (?, ?, ?, ?, ?, 1, 0, 'text')
            """
            cursor.execute(alt_query, values)
            connection.commit()
            print("Message stored successfully with alternative approach")
        
        cursor.close()
        print(f"Message stored: {sender} at {formatted_timestamp}")
        
    except Error as e:
        print(f"\nError storing message: {e}")
        print(f"Error code: {e.errno}")
        print(f"SQL state: {e.sqlstate}")
        print(f"Error message: {e.msg}")
        raise  # Re-raise the exception to see the full traceback
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise  # Re-raise the exception to see the full traceback

def store_transactions(connection, timestamp, sender, transactions):
    """Store extracted transactions in the MySQL database"""
    try:
        cursor = connection.cursor()
        
        for txn in transactions:
            price = txn.get("price", {})
            price_amount = price.get("amount") if isinstance(price, dict) else None
            price_currency = price.get("currency") if isinstance(price, dict) else None
            price_per_unit = price.get("per_unit") if isinstance(price, dict) else None
            
            region = txn.get("region", {})
            region_market = region.get("market") if isinstance(region, dict) else None
            region_warranty = region.get("warranty") if isinstance(region, dict) else None
            
            query = """
            INSERT INTO transactions (
                timestamp, sender, action, brand, product, model, storage, color,
                quantity, price_amount, price_currency, price_per_unit,
                region_market, region_warranty, `condition`, warranty,
                additional_details
            ) VALUES (
                STR_TO_DATE(%s, '%Y-%m-%d %H:%i:%s'), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            values = (
                timestamp,
                sender,
                txn.get("action"),
                txn.get("brand"),
                txn.get("product"),
                txn.get("model"),
                txn.get("storage"),
                txn.get("color"),
                txn.get("quantity", 1),
                price_amount,
                price_currency,
                price_per_unit,
                region_market,
                region_warranty,
                txn.get("condition"),
                txn.get("warranty"),
                txn.get("additional_details")
            )
            cursor.execute(query, values)
        
        connection.commit()
        print(f"{cursor.rowcount} transactions inserted successfully")
        cursor.close()
    except Error as e:
        print(f"Error storing transactions: {e}")