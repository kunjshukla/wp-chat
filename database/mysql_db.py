# database/mysql_db.py

import mysql.connector
from mysql.connector import Error
from config import config

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
        
        # Create messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(255),
            sender VARCHAR(255),
            content TEXT,
            bot_response TEXT,
            chat_jid VARCHAR(255)
        )
        """)
        
        # Create transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(255),
            sender VARCHAR(255),
            action VARCHAR(50),
            brand VARCHAR(255),
            product VARCHAR(255),
            model VARCHAR(255),
            storage VARCHAR(50),
            color VARCHAR(50),
            quantity INT,
            price_amount FLOAT,
            price_currency VARCHAR(10),
            price_per_unit BOOLEAN,
            region_market VARCHAR(255),
            region_warranty VARCHAR(255),
            condition VARCHAR(50),
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
        query = """
        INSERT INTO messages (timestamp, sender, content, bot_response, chat_jid)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (timestamp, sender, content, bot_response, chat_jid)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        print(f"Message stored: {sender} at {timestamp}")
    except Error as e:
        print(f"Error storing message: {e}")

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
                region_market, region_warranty, condition, warranty,
                additional_details
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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