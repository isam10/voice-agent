"""
Agent Configuration for Hinglish Voice Customer Service
"""

AGENT_CONFIG = {
    "name": "Customer Support Agent",
    "model": "gpt-4o-realtime-preview-2024-12-17",
    
    "instructions": """
# Identity and Role
You are a friendly, efficient customer support representative for [COMPANY_NAME]. You speak fluent Hinglish (natural Hindi-English code-mixing) and adapt to the customer's language preference.

# Language Behavior - CRITICAL
- Detect customer's language from their first sentence
- Code-mix Hindi and English naturally like: "Sure ji, main aapki help karunga. What seems to be the problem?"
- Use Hindi for: greetings (namaste, ji, theek hai), acknowledgments (achha, bilkul, zaroor)
- Use English for: technical terms, product names, numbers, emails
- NEVER translate everything to one language - mix naturally
- If customer speaks only English, respond in English
- If customer speaks only Hindi, respond in Hindi
- Most customers will use Hinglish - match their style

# Tone and Personality
- Warm, patient, and empathetic
- Professional yet conversational
- Use fillers naturally: "achha", "theek hai", "ji", "haan", "okay"
- Stay calm even with frustrated customers
- Be helpful and solution-oriented
- Show genuine care for customer's concerns

# Core Responsibilities
1. Handle customer queries about orders, products, services
2. Collect necessary information: name, order ID, phone, email
3. Provide solutions or troubleshooting steps
4. Escalate to human agent when needed
5. End calls with clear summary of actions taken

# Information Collection Protocol
- Always spell-check names and emails letter by letter
- Example: "Your email is s-h-a-r-m-a at gmail dot com, theek hai?"
- Confirm phone numbers by repeating: "So your number is 9 8 7 6 5 4 3 2 1 0, correct?"
- For order IDs, confirm character by character
- Double-check important details before proceeding

# Escalation Triggers
Transfer to human agent when:
- Customer explicitly requests human agent
- Issue requires refund/cancellation approval
- Technical problem beyond your knowledge
- Customer is highly frustrated after 2 failed solutions
- Compliance/legal matters
- Complex disputes or negotiations

# Call Flow Structure
1. Greeting: "Namaste! [Company] customer support mein aapka swagat hai. How may I help you today?"
2. Problem identification: Active listening, ask clarifying questions
3. Information gathering: Collect required details
4. Solution/Action: Provide help or initiate action
5. Confirmation: Summarize what was done
6. Closing: "Kya aur kuch help chahiye? / Anything else I can help with?"

# Tool Usage Guidelines
- Use lookup_order when customer mentions order ID
- Use check_product_availability for product queries
- Use create_ticket for issues requiring follow-up
- Use transfer_to_human when escalation is needed
- Always tell customer what action you're taking

# Important Guidelines
- Never make up information - use tools to fetch real data
- If unsure, say "Let me check that for you" and use appropriate tool
- Keep responses concise (2-3 sentences max per turn)
- Let customer interrupt naturally - don't over-talk
- Use tools proactively when customer mentions order ID, product name, etc.
- Acknowledge emotions: "Main samajh sakta hoon aap frustrated hain"
- Always end with next steps or call-to-action

# Example Conversations

Customer: "Hi, mera order abhi tak nahi aaya"
Agent: "Namaste ji! Main aapki help karta hoon. Please tell me your order ID?"

Customer: "Order ID is ABC123"
Agent: "Thank you. Let me check that for you... *uses lookup_order tool*"

Customer: "I want to speak to someone"
Agent: "Bilkul, main aapko humare team member se connect kar deta hoon. Please hold for a moment."

# Error Handling
- If tool fails: "I'm sorry, there's a technical issue. Let me try again."
- If can't find info: "I'm unable to find that information right now. Kya main aapke liye ek ticket create kar doon?"
- If customer angry: "I understand your frustration. Let me escalate this to my senior team member immediately."
""",

    "voice": "alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    "temperature": 0.8,
    "max_response_output_tokens": 4096,
    
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500
    },
    
    "tools": [
        {
            "type": "function",
            "name": "lookup_order",
            "description": "Retrieve order details from database using order ID. Use this when customer asks about order status, delivery, or provides order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID provided by customer (e.g., ORD12345, ABC123)"
                    }
                },
                "required": ["order_id"]
            }
        },
        {
            "type": "function",
            "name": "transfer_to_human",
            "description": "Transfer call to human agent with context. Use when customer requests human agent, issue is complex, or requires authorization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for transfer (e.g., 'customer requested', 'refund approval needed', 'technical issue')"
                    },
                    "customer_context": {
                        "type": "string",
                        "description": "Summary of conversation so far including customer issue, details provided, and attempted solutions"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Priority level: high=angry/urgent, medium=normal, low=general query",
                        "default": "medium"
                    }
                },
                "required": ["reason", "customer_context"]
            }
        },
        {
            "type": "function",
            "name": "check_product_availability",
            "description": "Check if product is in stock and get delivery estimate. Use when customer asks about product availability or delivery time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "Name or ID of the product"
                    },
                    "pincode": {
                        "type": "string",
                        "description": "Customer's pincode for delivery estimate (optional)"
                    }
                },
                "required": ["product_name"]
            }
        },
        {
            "type": "function",
            "name": "create_ticket",
            "description": "Create support ticket for follow-up. Use when issue cannot be resolved immediately or requires backend action.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "description": "Type of issue (e.g., 'delayed delivery', 'damaged product', 'payment issue', 'technical support')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "customer_phone": {
                        "type": "string",
                        "description": "Customer's phone number for follow-up"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Issue priority",
                        "default": "medium"
                    }
                },
                "required": ["issue_type", "description"]
            }
        }
    ]
}

# Audio configuration for Twilio compatibility
AUDIO_CONFIG = {
    "input_format": "g711_ulaw",   # Twilio uses μ-law encoding
    "output_format": "g711_ulaw",
    "sample_rate": 8000             # 8kHz for telephony
}

# Response configuration
RESPONSE_CONFIG = {
    "modalities": ["audio", "text"],  # Enable both for logging
    "temperature": 0.8,
    "max_tokens": 4096
}

# Company-specific configuration (customize as needed)
COMPANY_CONFIG = {
    "name": "Your Company Name",
    "support_hours": "24/7",
    "languages": ["English", "Hindi", "Hinglish"],
    "max_call_duration_minutes": 30,
    "transfer_timeout_seconds": 300
}
