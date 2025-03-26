import asyncio
import os
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv
from extend import ExtendClient

from extend_ai_toolkit.shared.functions import (
    get_virtual_cards,
    get_credit_cards,
    get_virtual_card_detail,
    create_virtual_card,
    update_virtual_card,
    cancel_virtual_card,
    close_virtual_card
)

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Skip all tests if environment variables are not set
pytestmark = pytest.mark.skipif(
    not all([
        os.getenv("EXTEND_API_KEY"),
        os.getenv("EXTEND_API_SECRET"),
        os.getenv("EXTEND_TEST_RECIPIENT"),
        os.getenv("EXTEND_TEST_CARDHOLDER")
    ]),
    reason="Integration tests require EXTEND_API_KEY, EXTEND_API_SECRET, EXTEND_TEST_RECIPIENT, and EXTEND_TEST_CARDHOLDER environment variables"
)


@pytest.fixture(scope="session")
def extend():
    """Create a real API client for integration testing"""
    api_key = os.getenv("EXTEND_API_KEY")
    api_secret = os.getenv("EXTEND_API_SECRET")
    return ExtendClient(api_key, api_secret)


@pytest.fixture(scope="session")
def test_recipient():
    """Get the test recipient email"""
    return os.getenv("EXTEND_TEST_RECIPIENT")


@pytest.fixture(scope="session")
def test_cardholder():
    """Get the test cardholder email"""
    return os.getenv("EXTEND_TEST_CARDHOLDER")


_cached_test_credit_card = None


@pytest.fixture(scope="session")
def test_credit_card(extend, event_loop):
    """Synchronous fixture that caches the first active credit card for testing."""
    global _cached_test_credit_card
    if _cached_test_credit_card is None:
        response = event_loop.run_until_complete(
            get_credit_cards(extend=extend, status="ACTIVE")
        )
        assert response.get("creditCards"), "No credit cards available for testing"
        _cached_test_credit_card = response["creditCards"][0]
    return _cached_test_credit_card


@pytest.mark.integration
class TestCreditCards:
    """Integration tests for credit card functions"""

    @pytest.mark.asyncio
    async def test_list_credit_cards(self, extend):
        """Test listing credit cards with various filters"""

        response = await get_credit_cards(extend=extend)
        assert "creditCards" in response

        # List with pagination
        response = await get_credit_cards(
            extend=extend,
            page=1,
            per_page=10
        )
        assert len(response["creditCards"]) <= 10

        # List with status filter
        response = await get_credit_cards(
            extend=extend,
            status="ACTIVE"
        )
        for card in response["creditCards"]:
            assert card["status"] == "ACTIVE"


@pytest.mark.integration
class TestVirtualCards:
    """Integration tests for virtual card operations"""

    @pytest.mark.asyncio
    async def test_virtual_card_lifecycle(self, extend, test_credit_card, test_recipient, test_cardholder):
        """Test creating, retrieving, updating, and canceling a virtual card"""
        # Calculate valid_to date (3 months from today)
        valid_to = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%dT23:59:59.999Z")

        test_cc = test_credit_card

        # Create a simple virtual card without recurrence
        response = await create_virtual_card(
            extend=extend,
            credit_card_id=test_cc["id"],
            display_name="Integration Test Card",
            amount_dollars=1,
            notes="Created by integration test",
            is_recurring=False,
            recipient_email=test_recipient,
            cardholder_email=test_cardholder,
            valid_to=valid_to
        )

        card = response["virtualCard"]
        assert card["status"] == "ACTIVE"
        assert card["displayName"] == "Integration Test Card"
        assert card["balanceCents"] == 100
        assert card["recurs"] is False
        assert card["notes"] == "Created by integration test"

        # Store card ID for subsequent tests
        card_id = card["id"]

        # Get the card details
        get_response = await get_virtual_card_detail(extend=extend, virtual_card_id=card_id)
        assert get_response["virtualCard"]["id"] == card_id

        # Update the card
        update_response = await update_virtual_card(
            extend=extend,
            virtual_card_id=card_id,
            display_name="Updated Test Card",
            notes="Updated by integration test",
            balance_dollars=200
        )

        updated_card = update_response["virtualCard"]
        assert updated_card["status"] == "ACTIVE"
        assert updated_card["displayName"] == "Updated Test Card"
        assert updated_card["balanceCents"] == 20000
        assert updated_card["notes"] == "Updated by integration test"

        # Cancel the card
        cancel_response = await cancel_virtual_card(extend=extend, virtual_card_id=card_id)
        assert cancel_response["virtualCard"]["status"] == "CANCELLED"

        # Close the card (cleanup)
        close_response = await close_virtual_card(extend=extend, virtual_card_id=card_id)
        assert close_response["virtualCard"]["status"] == "CLOSED"

    @pytest.mark.asyncio
    async def test_list_virtual_cards(self, extend):
        """Test listing virtual cards with various filters"""

        response = await get_virtual_cards(extend)
        assert "virtualCards" in response

        # List with pagination
        response = await get_virtual_cards(
            extend=extend,
            page=1,
            per_page=10
        )
        assert len(response["virtualCards"]) <= 10

        # List with status filter
        response = await get_virtual_cards(
            extend=extend,
            status="CLOSED"
        )
        for card in response["virtualCards"]:
            assert card["status"] == "CLOSED"


@pytest.mark.integration
class TestTransactions:
    """Integration tests for transaction operations"""

    @pytest.mark.asyncio
    async def test_list_transactions(self, extend):
        """Test listing transactions with various filters"""
        # Get transactions
        response = await extend.transactions.get_transactions()

        # Verify response structure
        assert isinstance(response, dict), "Response should be a dictionary"
        assert "transactions" in response, "Response should contain 'transactions' key"
        assert isinstance(response["transactions"], list), "Transactions should be a list"

        # If there are transactions, verify their structure
        if response["transactions"]:
            transaction = response["transactions"][0]
            required_fields = ["id", "status", "virtualCardId", "merchantName", "type", "authBillingAmountCents"]
            for field in required_fields:
                assert field in transaction, f"Transaction should contain '{field}' field"


@pytest.mark.integration
class TestRecurringCards:
    """Integration tests for recurring virtual cards"""

    @pytest.mark.asyncio
    async def test_create_recurring_card(self, extend, test_credit_card, test_recipient, test_cardholder):
        """Test creating a daily recurring card"""
        next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT23:59:59.999Z")
        test_cc = test_credit_card

        # Create a daily recurring card
        response = await create_virtual_card(
            extend=extend,
            credit_card_id=test_cc["id"],
            display_name="Daily Recurring Test Card",
            amount_dollars=1,
            notes="Created by integration test",
            is_recurring=True,
            recipient_email=test_recipient,
            cardholder_email=test_cardholder,
            period="DAILY",
            interval=1,
            terminator="DATE",
            until=next_month
        )

        card = response["virtualCard"]
        assert card["status"] == "ACTIVE"
        assert card["displayName"] == "Daily Recurring Test Card"
        assert card["balanceCents"] == 100
        assert card["recurs"] is True
        assert card["recurrence"]["period"] == "DAILY"
        assert card["recurrence"]["interval"] == 1
        assert card["recurrence"]["terminator"] == "DATE"
        # Normalize timezone format before comparison
        expected_date = next_month.replace("Z", "+0000")
        assert card["recurrence"]["until"] == expected_date

        # Store card ID for cleanup
        card_id = card["id"]

        # Clean up by cancelling and closing
        cancel_response = await cancel_virtual_card(extend=extend, virtual_card_id=card_id)
        assert cancel_response["virtualCard"]["status"] == "CANCELLED"

        close_response = await close_virtual_card(extend=extend, virtual_card_id=card_id)
        assert close_response["virtualCard"]["status"] == "CLOSED"


def test_environment_variables():
    """Test that required environment variables are set"""
    assert os.getenv("EXTEND_API_KEY"), "EXTEND_API_KEY environment variable is required"
    assert os.getenv("EXTEND_API_SECRET"), "EXTEND_API_SECRET environment variable is required"
