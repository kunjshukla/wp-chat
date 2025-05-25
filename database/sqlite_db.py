# database/sqlite_db.py

import sqlite3
import os
import sys
from config import config

def setup_sqlite_database():
    """Set up the SQLite database and ensure the correct schema"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config.MESSAGES_DB_PATH), exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect(config.MESSAGES_DB_PATH)
        cursor = conn.cursor()
        
        # Check if messages table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='messages'
        """)
        table_exists = cursor.fetchone() is not None
        
        # Define the required columns (aligned with main.go schema)
        required_columns = {
            'id': 'TEXT',
            'chat_jid': 'TEXT',
            'sender': 'TEXT NOT NULL',
            'content': 'TEXT NOT NULL',
            'timestamp': 'TEXT',
            'is_from_me': 'BOOLEAN',
            'media_type': 'TEXT',  # Always 'text' from main.go
            'processed': 'BOOLEAN DEFAULT 0'  # Added by our script
        }
        
        if not table_exists:
            # Create messages table with all required columns
            columns_def = ', '.join([f"{col} {col_type}" for col, col_type in required_columns.items()])
            cursor.execute(f"""
            CREATE TABLE messages ({columns_def}, PRIMARY KEY (id, chat_jid))
            """)
            print("Created messages table with all required columns")
        else:
            # Check existing columns
            cursor.execute("PRAGMA table_info(messages)")
            existing_columns = {column[1]: column[2] for column in cursor.fetchall()}
            
            # Check for missing columns and add them
            for col, col_type in required_columns.items():
                if col not in existing_columns:
                    cursor.execute(f"""
                    ALTER TABLE messages 
                    ADD COLUMN {col} {col_type.split(' ')[0]}
                    """)
                    print(f"Added missing column: {col}")
            
            # Verify all required columns are present
            cursor.execute("PRAGMA table_info(messages)")
            final_columns = {column[1]: column[2] for column in cursor.fetchall()}
            missing = [col for col in required_columns if col not in final_columns]
            if missing:
                print(f"Error: Could not add columns {missing}. Recreating table...")
                cursor.execute("ALTER TABLE messages RENAME TO messages_backup")
                columns_def = ', '.join([f"{col} {col_type}" for col, col_type in required_columns.items()])
                cursor.execute(f"""
                CREATE TABLE messages ({columns_def}, PRIMARY KEY (id, chat_jid))
                """)
                common_columns = [col for col in existing_columns if col in required_columns]
                if common_columns:
                    columns_list = ', '.join(common_columns)
                    cursor.execute(f"""
                    INSERT INTO messages ({columns_list})
                    SELECT {columns_list} FROM messages_backup
                    """)
                cursor.execute("DROP TABLE messages_backup")
                print("Recreated messages table with all required columns")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"SQLite database initialized at {config.MESSAGES_DB_PATH}")
        
    except sqlite3.Error as e:
        print(f"Error setting up SQLite database: {e}")
        sys.exit(1)