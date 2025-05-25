# services/message_service.py

from services.gemini_service import extract_transactions_with_gemini, call_gemini_api

def process_message(message):
    """Process the user message to extract transaction details or generate a response"""
    transaction_data = extract_transactions_with_gemini(message)
    transactions = transaction_data["transactions"]
    
    if transactions:
        responses = []
        for txn in transactions:
            response = [f"Detected transaction: {txn['action'].upper()}"]
            product_details = [txn['brand'], txn['product']]
            if txn.get('model'): product_details.append(txn['model'])
            if txn.get('storage'): product_details.append(txn['storage'])
            if txn.get('color'): product_details.append(txn['color'])
            response.append("Product: " + " ".join(filter(None, product_details)))
            response.append(f"Quantity: {txn['quantity']} units")
            if txn.get('price', {}).get('amount'):
                price = txn['price']
                price_str = f"{price['amount']} {price.get('currency', 'USD')}"
                if price.get('per_unit'):
                    price_str += " per unit"
                response.append(f"Price: {price_str}")
            if txn.get('region', {}).get('market'):
                response.append(f"Market: {txn['region']['market']}")
            if txn.get('warranty'):
                response.append(f"Warranty: {txn['warranty']}")
            if txn.get('additional_details'):
                response.append(f"Additional Info: {txn['additional_details']}")
            responses.append("\n".join(response))
        return "\n\n".join(responses), transactions
    else:
        general_prompt = """
        You are a helpful WhatsApp trading bot. Respond to the user's message in a friendly and concise manner.
        If the user asks about buying or selling, suggest they provide more details including:
        - Brand and product name
        - Model/variant and storage capacity
        - Color preference
        - Quantity needed
        - Price expectations
        - Region/market
        - Warranty requirements
        """
        bot_response = call_gemini_api(message, general_prompt)
        return bot_response, []