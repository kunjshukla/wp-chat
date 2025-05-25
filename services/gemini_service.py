# services/gemini_service.py

import google.generativeai as genai
import json
import time
from config import config

def setup_gemini():
    """Configure the Gemini API"""
    genai.configure(api_key=config.GEMINI_API_KEY)

def call_gemini_api(chat_text, prompt):
    """Call Gemini API to process the message and generate a response"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{prompt}\n\nUser Message:\n{chat_text}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        if "Quota exceeded" in str(e):
            print("Gemini API quota exceeded. Waiting 60 seconds before retrying...")
            time.sleep(60)
            return call_gemini_api(chat_text, prompt)
        return "Sorry, I encountered an error while processing your request."

def extract_transactions_with_gemini(message):
    """Extract transaction details from a WhatsApp message using Gemini"""
    prompt = """
    You are an AI assistant specialized in extracting detailed product trade information from WhatsApp messages. 
    Your task is to carefully analyze messages for product trading intent and extract ALL available details.

    Common trading indicators:
    - "WTB" (want to buy), "WTS" (want to sell)
    - "Available", "Require", "Need stock"
    - "Selling", "Buying", "Looking for"
    - Price indicators: "$", "USD", "per unit", "each"
    - Quantity indicators: "pcs", "units", "qty", "pieces"

    For EACH product mentioned, extract these details:
    1. Action: "buy" or "sell" (required)
    2. Brand: The brand name (required)
    3. Product: Full product name (required)
    4. Model/Variant: Specific model number or variant
    5. Memory/Storage: Storage capacity (e.g., "128GB", "512GB")
    6. Color: Product color (if mentioned)
    7. Quantity: Number of units (required, default to 1 if not specified)
    8. Price: 
       - Per unit price
       - Currency (USD, EUR, etc.)
       - Any bulk pricing if mentioned
    9. Region: 
       - Country/region of origin
       - Shipping destination
       - Market region (e.g., "Global", "EU", "US")
    10. Condition: New/Used/Refurbished
    11. Warranty: Warranty information if mentioned
    12. Additional Details: Any other relevant specifications

    Example input:
    "WTS Samsung Z Flip 5 512GB Beige, 30 units available at $850 each. Global warranty, EU region. Also have Graphite color same specs."

    Example output:
    {
      "transactions": [
        {
          "action": "sell",
          "brand": "Samsung",
          "product": "Z Flip 5",
          "model": "Z Flip 5",
          "storage": "512GB",
          "color": "Beige",
          "quantity": 30,
          "price": {
            "amount": 850,
            "currency": "USD",
            "per_unit": true
          },
          "region": {
            "market": "EU",
            "warranty": "Global"
          },
          "condition": "New",
          "warranty": "Global",
          "additional_details": "Available in Graphite color with same specifications"
        },
        {
          "action": "sell",
          "brand": "Samsung",
          "product": "Z Flip 5",
          "model": "Z Flip 5",
          "storage": "512GB",
          "color": "Graphite",
          "quantity": 30,
          "price": {
            "amount": 850,
            "currency": "USD",
            "per_unit": true
          },
          "region": {
            "market": "EU",
            "warranty": "Global"
          },
          "condition": "New",
          "warranty": "Global",
          "additional_details": "Same specifications as Beige variant"
        }
      ]
    }

    Important rules:
    1. Extract ALL available details - don't skip any mentioned information
    2. If a detail is not mentioned, use null or empty string
    3. For multiple products, create separate transaction objects
    4. Maintain consistency in units (e.g., always use USD for currency)
    5. Include any additional context that might be relevant
    6. If the message doesn't contain trading intent, return empty transactions list
    """
    
    gemini_response = call_gemini_api(message, prompt)
    if gemini_response:
        try:
            cleaned_response = gemini_response.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            print("Error: Gemini transaction response is not valid JSON.")
            return {"transactions": []}
    return {"transactions": []}