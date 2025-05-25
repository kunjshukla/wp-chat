# services/response_service.py

import requests
from config import config

def send_response(sender_jid, response):
    """Send a response back to the WhatsApp user via the MCP server"""
    try:
        payload = {
            "name": "send_message",
            "arguments": {
                "jid": sender_jid,
                "message": response
            }
        }
        response = requests.post(config.MCP_SERVER_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"Sent response to {sender_jid}: {response.json()}")
        else:
            print(f"Failed to send response to {sender_jid}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending response: {str(e)}")