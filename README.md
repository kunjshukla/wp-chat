# wp-chat



# WhatsApp Trading Bot

A WhatsApp bot that monitors messages, processes trading-related content, and stores data in both SQLite and MySQL databases.

## Prerequisites

- Python 3.10 or higher
- Go 1.16 or higher
- MySQL Server
- WhatsApp account (phone number)

## System Requirements

- Linux/Unix-based system (tested on Ubuntu)
- At least 2GB RAM
- Internet connection for WhatsApp

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wp-chat
```

2. Set up MySQL:
```bash
# Install MySQL if not already installed
sudo apt-get update
sudo apt-get install mysql-server

# Start MySQL service
sudo systemctl start mysql

# Create database and user
mysql -u root -p
```
```sql
CREATE DATABASE whatsapp_trading_db;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin123';
FLUSH PRIVILEGES;
```

3. Set up Python environment:
```bash
# Create and activate virtual environment for MCP server
cd whatsapp-mcp/whatsapp-mcp-server
python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install mysql-connector-python mcp-server requests
```

4. Set up Go environment:
```bash
# Install Go dependencies for WhatsApp bridge
cd ../whatsapp-bridge
go mod download
```

## Configuration

1. Update MySQL credentials in `config/config.py` if different from defaults:
```python
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "whatsapp_trading_db"
}
```

2. Update Gemini API key in `config/config.py`:
```python
GEMINI_API_KEY = "your-gemini-api-key-here"
```

## Running the Application

The application consists of three main components that need to be running:

1. Start the WhatsApp Bridge (Go service):
```bash
cd whatsapp-mcp/whatsapp-bridge
go run main.go
```
- On first run, scan the QR code with your WhatsApp to connect
- The bridge will store messages in SQLite database

2. Start the MCP Server (Python service):
```bash
cd whatsapp-mcp/whatsapp-mcp-server
source .venv/bin/activate
python main.py
```
- This service connects to the WhatsApp bridge
- Processes messages and stores them in MySQL
- Handles bot responses

3. Start the Monitor Service (optional, for additional monitoring):
```bash
cd /path/to/project
python services/whatsapp_monitor.py
```
- Monitors messages and ensures they are stored in MySQL
- Provides additional logging and error handling

## Database Structure

### SQLite Database (WhatsApp Bridge)
- Location: `whatsapp-mcp/whatsapp-bridge/store/messages.db`
- Tables:
  - `messages`: Raw WhatsApp messages
  - `chats`: Chat information

### MySQL Database
- Database: `whatsapp_trading_db`
- Tables:
  - `messages`: Processed messages with bot responses
  - `transactions`: Extracted trading information

## Message Flow

1. WhatsApp message received → WhatsApp Bridge (SQLite)
2. MCP Server processes message → MySQL Database
3. Bot generates response → Sent back to WhatsApp
4. Transaction data (if any) → Stored in MySQL

## Troubleshooting

1. Database Connection Issues:
   - Check MySQL service is running: `sudo systemctl status mysql`
   - Verify credentials in `config/config.py`
   - Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

2. WhatsApp Bridge Issues:
   - Check if bridge is running: `ps aux | grep whatsapp-bridge`
   - Verify QR code scanning
   - Check bridge logs for connection errors

3. MCP Server Issues:
   - Ensure virtual environment is activated
   - Check all Python dependencies are installed
   - Verify MySQL connection

4. Common Errors:
   - "datatype mismatch": Check MySQL schema matches expected format
   - "connection refused": Ensure all services are running
   - "QR code expired": Restart WhatsApp bridge

## Development

- Python code is in `whatsapp-mcp/whatsapp-mcp-server/`
- Go code is in `whatsapp-mcp/whatsapp-bridge/`
- Database schemas can be modified in respective files:
  - SQLite: `database/sqlite_db.py`
  - MySQL: `database/mysql_db.py`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
