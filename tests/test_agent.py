"""
Unit Tests for Voice Agent
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import application modules
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.database_service import DatabaseService
from services.openai_service import OpenAIService
from services.twilio_service import TwilioService
from utils.helpers import (
    sanitize_phone_number,
    validate_email,
    validate_indian_phone,
    generate_session_id,
    parse_hinglish_input,
    detect_language,
    estimate_call_cost
)


class TestHelpers:
    """Test helper functions"""
    
    def test_sanitize_phone_number(self):
        """Test phone number sanitization"""
        assert sanitize_phone_number("9876543210") == "+919876543210"
        assert sanitize_phone_number("+91 9876543210") == "+919876543210"
        assert sanitize_phone_number("(987) 654-3210") == "+919876543210"
    
    def test_validate_email(self):
        """Test email validation"""
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.in") == True
        assert validate_email("invalid.email") == False
        assert validate_email("@domain.com") == False
    
    def test_validate_indian_phone(self):
        """Test Indian phone number validation"""
        assert validate_indian_phone("9876543210") == True
        assert validate_indian_phone("919876543210") == True
        assert validate_indian_phone("+91 9876543210") == True
        assert validate_indian_phone("1234567890") == False
        assert validate_indian_phone("987654321") == False
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id = generate_session_id()
        assert session_id.startswith("sess_")
        assert len(session_id) > 10
        
        # Ensure uniqueness
        session_id2 = generate_session_id()
        assert session_id != session_id2
    
    def test_parse_hinglish_input(self):
        """Test Hinglish text parsing"""
        text = "Mera order ID ABC123 hai aur phone 9876543210 hai"
        result = parse_hinglish_input(text)
        
        assert "ABC123" in result["order_ids"]
        assert "9876543210" in result["phone_numbers"]
    
    def test_detect_language(self):
        """Test language detection"""
        assert detect_language("Hello, how are you?") == "en"
        assert detect_language("Namaste ji, kaise hain?") == "hinglish"
        assert detect_language("") == "unknown"
    
    def test_estimate_call_cost(self):
        """Test call cost estimation"""
        cost = estimate_call_cost(60)  # 1 minute
        
        assert "duration_minutes" in cost
        assert "total_cost_usd" in cost
        assert cost["duration_minutes"] == 1.0
        assert cost["total_cost_usd"] > 0


class TestDatabaseService:
    """Test database service"""
    
    @pytest.fixture
    def db_service(self):
        """Create database service instance"""
        return DatabaseService()
    
    @pytest.mark.asyncio
    async def test_create_call_record(self, db_service):
        """Test call record creation"""
        call_sid = "CA1234567890"
        call_data = {
            "from": "+919876543210",
            "to": "+911234567890",
            "streamSid": "MZ1234567890"
        }
        
        record = await db_service.create_call_record(call_sid, call_data)
        
        assert record["call_sid"] == call_sid
        assert record["status"] == "in-progress"
        assert "start_time" in record
    
    @pytest.mark.asyncio
    async def test_get_order_details(self, db_service):
        """Test order lookup"""
        order_id = "ORD123"
        order = await db_service.get_order_details(order_id)
        
        assert order["order_id"] == order_id
        assert "status" in order
        assert "items" in order
    
    @pytest.mark.asyncio
    async def test_check_inventory(self, db_service):
        """Test inventory check"""
        product = "Test Product"
        result = await db_service.check_inventory(product, "400001")
        
        assert result["product"] == product
        assert "available" in result
        assert "delivery_estimate" in result
    
    @pytest.mark.asyncio
    async def test_create_support_ticket(self, db_service):
        """Test ticket creation"""
        ticket = await db_service.create_support_ticket(
            call_sid="CA123",
            issue_type="delayed_delivery",
            description="Order not received",
            customer_phone="+919876543210"
        )
        
        assert "ticket_id" in ticket
        assert ticket["status"] == "open"


class TestTwilioService:
    """Test Twilio service"""
    
    @pytest.fixture
    def twilio_service(self):
        """Create Twilio service instance"""
        return TwilioService(
            account_sid="AC_TEST",
            auth_token="test_token",
            phone_number="+911234567890"
        )
    
    def test_generate_connect_twiml(self, twilio_service):
        """Test TwiML generation"""
        twiml = twilio_service.generate_connect_twiml(
            stream_url="wss://example.com/stream",
            call_sid="CA123",
            from_number="+919876543210"
        )
        
        assert "<?xml version" in twiml
        assert "<Response>" in twiml
        assert "<Connect>" in twiml
        assert "<Stream" in twiml
        assert "wss://example.com/stream" in twiml


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_call_flow(self):
        """Test complete call flow simulation"""
        db_service = DatabaseService()
        
        # Create call
        call_sid = "CA_TEST_123"
        call_data = {
            "from": "+919876543210",
            "to": "+911234567890",
            "streamSid": "MZ123"
        }
        
        # Start call
        record = await db_service.create_call_record(call_sid, call_data)
        assert record["status"] == "in-progress"
        
        # Simulate function calls
        order_result = await db_service.get_order_details("ORD123")
        assert "order_id" in order_result
        
        # End call
        await db_service.end_call_record(call_sid)
        final_record = await db_service.get_call_record(call_sid)
        assert final_record["status"] == "completed"


@pytest.mark.asyncio
async def test_concurrent_calls():
    """Test handling multiple concurrent calls"""
    db_service = DatabaseService()
    
    # Create multiple calls simultaneously
    call_tasks = []
    for i in range(5):
        call_sid = f"CA_TEST_{i}"
        call_data = {"from": f"+9198765432{i}0", "to": "+911234567890"}
        task = db_service.create_call_record(call_sid, call_data)
        call_tasks.append(task)
    
    # Wait for all calls to be created
    results = await asyncio.gather(*call_tasks)
    
    assert len(results) == 5
    for result in results:
        assert result["status"] == "in-progress"


def test_hinglish_scenarios():
    """Test various Hinglish conversation scenarios"""
    test_cases = [
        {
            "input": "Mera order ABC123 ka status kya hai?",
            "expected_entities": {"order_ids": ["ABC123"]}
        },
        {
            "input": "Please call me on 9876543210",
            "expected_entities": {"phone_numbers": ["9876543210"]}
        },
        {
            "input": "My email is test@example.com aur phone 9876543210",
            "expected_entities": {
                "emails": ["test@example.com"],
                "phone_numbers": ["9876543210"]
            }
        }
    ]
    
    for case in test_cases:
        result = parse_hinglish_input(case["input"])
        
        for entity_type, expected_values in case["expected_entities"].items():
            assert len(result[entity_type]) > 0
            for expected in expected_values:
                assert expected in result[entity_type]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
