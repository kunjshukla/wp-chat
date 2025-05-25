# main.py

import sqlite3
import time
import os
from datetime import datetime
from database.sqlite_db import setup_sqlite_database
from database.mysql_db import create_mysql_connection, store_message, store_transactions
from services.gemini_service import setup_gemini
from services.message_service import process_message
from services.response_service import send_response
from config import config

def monitor_whatsapp_messages():
    """Monitor the WhatsApp SQLite database for new messages"""
    # Setup databases
    setup_sqlite_database()
    mysql_conn = create_mysql_connection()
    if mysql_conn is None:
        print("Failed to connect to MySQL. Exiting...")
        return
    
    # Setup Gemini API
    setup_gemini()
    
    print(f"Monitoring WhatsApp messages at {config.MESSAGES_DB_PATH}")
    
    while True:
        try:
            if not os.path.exists(config.MESSAGES_DB_PATH):
                print(f"SQLite database not found at {config.MESSAGES_DB_PATH}")
                time.sleep(5)
                continue
            
            # Ensure the SQLite schema is correct
            setup_sqlite_database()
            
            conn = sqlite3.connect(config.MESSAGES_DB_PATH)
            cursor = conn.cursor()
            
            query = """
            SELECT id, sender, content, jid, timestamp, chat_jid, is_from_me
            FROM messages
            WHERE processed = 0
            ORDER BY timestamp ASC
            """
            cursor.execute(query)
            new_messages = cursor.fetchall()
            
            if new_messages:
                print(f"Found {len(new_messages)} new messages")
                for msg in new_messages:
                    msg_id, sender, content, jid, timestamp, chat_jid, is_from_me = msg
                    try:
                        print(f"Processing message from {sender}: {content[:100]}... (is_from_me: {is_from_me})")
                        if not timestamp:
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        bot_response, transactions = process_message(content)
                        store_message(mysql_conn, timestamp, sender, content, bot_response, chat_jid)
                        if transactions:
                            store_transactions(mysql_conn, timestamp, sender, transactions)
                        if jid:
                            send_response(jid, bot_response)
                        cursor.execute("UPDATE messages SET processed = 1 WHERE id = ?", (msg_id,))
                        conn.commit()
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        continue
            
            conn.close()
        
        except sqlite3.Error as e:
            print(f"SQLite database error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(5)
        
        time.sleep(5)
    
    if mysql_conn.is_connected():
        mysql_conn.close()
        print("MySQL connection closed")

if __name__ == "__main__":
    print("WhatsApp trading bot started.")
    monitor_whatsapp_messages()