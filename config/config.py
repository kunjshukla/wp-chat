import os

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyDoBJCMwWDixx6RCrCj-J5fvKru6JSWtxo"  # Replace with your actual Gemini API key

# WhatsApp MCP Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_DB_PATH = os.path.join(BASE_DIR, "..", "whatsapp-mcp", "whatsapp-bridge", "store", "messages.db")

# MCP Server URL
MCP_SERVER_URL = "http://localhost:8000/mcp/callTool"

# MySQL Database Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "whatsapp_trading_db"
}