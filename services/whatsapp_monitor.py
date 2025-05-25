# services/whatsapp_monitor.py

import time
import requests
from datetime import datetime
from database.mysql_db import create_mysql_connection, store_message, store_transactions
from services.message_service import process_message

class WhatsAppMonitor:
    def __init__(self):
        self.mysql_conn = create_mysql_connection()
        if self.mysql_conn is None:
            raise Exception("Failed to connect to MySQL database")
        
        self.last_check = None
        self.mcp_server_url = "http://localhost:8000/mcp/callTool"
    
    def get_messages(self, after=None):
        """Get messages from WhatsApp MCP server"""
        try:
            response = requests.post(
                self.mcp_server_url,
                json={
                    "name": "list_messages",
                    "args": {
                        "after": after,
                        "limit": 100,
                        "include_context": False
                    }
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def process_message(self, message):
        """Process and store a message"""
        try:
            timestamp = message.get("timestamp")
            sender = message.get("sender")
            content = message.get("content")
            chat_jid = message.get("chat_jid")
            
            if not all([timestamp, sender, content, chat_jid]):
                print(f"Skipping incomplete message: {message}")
                return
            
            # Process message to get bot response and transactions
            bot_response, transactions = process_message(content)
            
            # Store message
            store_message(
                self.mysql_conn,
                timestamp,
                sender,
                content,
                bot_response,
                chat_jid
            )
            
            # Store transactions if any
            if transactions:
                store_transactions(
                    self.mysql_conn,
                    timestamp,
                    sender,
                    transactions
                )
            
            print(f"Processed message from {sender} at {timestamp}")
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def monitor(self):
        """Monitor WhatsApp messages continuously"""
        print("Starting WhatsApp message monitor...")
        
        while True:
            try:
                # Get messages since last check
                messages = self.get_messages(after=self.last_check)
                
                if messages:
                    print(f"Found {len(messages)} new messages")
                    for message in messages:
                        self.process_message(message)
                    
                    # Update last check time
                    self.last_check = datetime.now().isoformat()
                
                # Wait before next check
                time.sleep(5)
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    def close(self):
        """Close database connection"""
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    monitor = WhatsAppMonitor()
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        print("\nStopping WhatsApp monitor...")
    finally:
        monitor.close() 