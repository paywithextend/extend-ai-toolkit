import asyncio
import os
import tempfile
import uuid

import httpx
import pytest
from dotenv import load_dotenv
from extend import ExtendClient

from extend_ai_toolkit.shared.functions import (
    get_virtual_cards,
    get_credit_cards,
    create_expense_category,
    create_expense_category_label,
    get_expense_category_labels,
    update_expense_category_label,
    get_expense_categories,
    get_expense_category,
    update_expense_category,
    get_transactions,
    update_transaction_expense_data,
    create_receipt_attachment, automatch_receipts, send_receipt_reminder
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
        os.environ.get("EXTEND_API_KEY"),
        os.environ.get("EXTEND_API_SECRET"),
        os.environ.get("EXTEND_TEST_RECIPIENT"),
        os.environ.get("EXTEND_TEST_CARDHOLDER")
    ]),
    reason="Integration tests require EXTEND_API_KEY, EXTEND_API_SECRET, EXTEND_TEST_RECIPIENT, and EXTEND_TEST_CARDHOLDER environment variables"
)


@pytest.fixture(scope="session")
def extend():
    """Create a real API client for integration testing"""
    api_key = os.environ.get("EXTEND_API_KEY")
    api_secret = os.environ.get("EXTEND_API_SECRET")
    return ExtendClient(api_key, api_secret)


@pytest.fixture(scope="session")
def test_recipient():
    """Get the test recipient email"""
    return os.environ.get("EXTEND_TEST_RECIPIENT")


@pytest.fixture(scope="session")
def test_cardholder():
    """Get the test cardholder email"""
    return os.environ.get("EXTEND_TEST_CARDHOLDER")


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
        response = await get_transactions(extend)

        # Verify response structure
        assert isinstance(response, dict), "Response should be a dictionary"
        assert "report" in response, "Response should contain 'report' key"
        assert "transactions" in response["report"], "Report should contain 'transactions' key"
        assert isinstance(response["report"]["transactions"], list), "Transactions should be a list"

    @pytest.mark.asyncio
    async def test_update_transaction_expense_data(self, extend):
        """Test updating transaction expense data"""
        # Get a single transaction
        transactions_response = await get_transactions(extend, page=0, per_page=1, sort_field="createdAt")
        assert "transactions" in transactions_response["report"]
        transaction = transactions_response["report"]["transactions"][0]
        transaction_id = transaction["id"]

        # Update the transaction to have no expense categories
        data_no_expense_categories = {
            "expenseDetails": []
        }
        response_no_expense_categories = await update_transaction_expense_data(
            extend,
            transaction_id,
            user_confirmed_data_values=True,
            data=data_no_expense_categories
        )
        assert isinstance(response_no_expense_categories, dict), "Response should be a dictionary"
        assert response_no_expense_categories["id"] == transaction_id, "Transaction ID should match the input"
        assert "expenseCategories" not in response_no_expense_categories, "Expense categories should not exist on response"

        # Get an expense category and one of its labels
        expense_categories_response = await get_expense_categories(extend=extend, active=True)
        assert "expenseCategories" in expense_categories_response, "No expense categories found"
        expense_category = expense_categories_response["expenseCategories"][0]
        category_id = expense_category["id"]

        expense_category_labels_response = await get_expense_category_labels(extend, category_id=category_id)
        if not expense_category_labels_response.get("expenseLabels"):
            # Create a new label if none exist
            label_name = f"Test Label {str(uuid.uuid4())[:8]}"
            label_code = f"LBL{str(uuid.uuid4())[:8]}"
            expense_label_response = await create_expense_category_label(
                extend=extend,
                category_id=category_id,
                name=label_name,
                code=label_code,
                active=True
            )
            expense_label = expense_label_response
        else:
            expense_label = expense_category_labels_response["expenseLabels"][0]

        # Update the transaction with an expense category and one of its labels
        data_with_expense_category = {
            "expenseDetails": [
                {
                    "categoryId": expense_category["id"],
                    "labelId": expense_label["id"]
                }
            ]
        }
        response_with_expense_category = await update_transaction_expense_data(
            extend=extend,
            transaction_id=transaction_id,
            user_confirmed_data_values=True,
            data=data_with_expense_category
        )
        assert isinstance(response_with_expense_category, dict), "Response should be a dictionary"
        assert response_with_expense_category["id"] == transaction_id, "Transaction ID should match the input"
        assert len(response_with_expense_category[
                       "expenseCategories"]) == 1, "Transaction should have only one expense category coding"
        coded_expense_category = response_with_expense_category["expenseCategories"][0]
        assert coded_expense_category["categoryId"] == expense_category[
            "id"], "Expense categories should match the input"
        assert coded_expense_category["labelId"] == expense_label["id"], "Expense categories should match the input"


@pytest.mark.integration
class TestExpenseData:
    """Integration tests for expense category and label endpoints"""

    @pytest.mark.asyncio
    async def test_list_expense_categories(self, extend):
        """Test getting a list of expense categories"""
        response = await get_expense_categories(extend=extend)
        # Adjust the key based on your API's response structure
        assert isinstance(response, dict)
        # Example: if your response contains a key "expenseCategories"
        assert "expenseCategories" in response or "categories" in response

    @pytest.mark.asyncio
    async def test_create_and_get_expense_category(self, extend):
        """Test creating an expense category and then retrieving it"""
        # Create a new expense category with unique values
        category_name = f"Integration Test Category {str(uuid.uuid4())[:8]}"
        category_code = f"ITC{str(uuid.uuid4())[:8]}"
        create_response = await create_expense_category(
            extend=extend,
            name=category_name,
            code=category_code,
            required=True,
            active=True,
            free_text_allowed=False,
        )
        category = create_response
        assert category, "Expense category creation failed"
        category_id = category["id"]

        # Retrieve the created category
        get_response = await get_expense_category(extend=extend, category_id=category_id)
        retrieved_category = get_response
        assert retrieved_category, "Expense category retrieval failed"
        assert retrieved_category["id"] == category_id

    @pytest.mark.asyncio
    async def test_update_expense_category(self, extend):
        """Test updating an expense category"""
        category_name = f"Integration Test Category {str(uuid.uuid4())[:8]}"
        category_code = f"ITC{str(uuid.uuid4())[:8]}"
        create_response = await create_expense_category(
            extend=extend,
            name=category_name,
            code=category_code,
            required=False,
            active=True,
            free_text_allowed=False,
        )
        category = create_response
        category_id = category["id"]

        # Update the expense category
        new_name = f"Updated Category {str(uuid.uuid4())[:8]}"
        update_response = await update_expense_category(
            extend=extend,
            category_id=category_id,
            name=new_name,
            active=False,
            required=False,
            free_text_allowed=True,
        )
        updated_category = update_response
        assert updated_category, "Expense category update failed"
        assert updated_category["name"] == new_name
        assert updated_category["active"] is False

    @pytest.mark.asyncio
    async def test_create_and_list_expense_category_labels(self, extend):
        """Test creating an expense category label and listing labels for a category"""
        # Create a new expense category first
        category_name = f"Integration Test Category {str(uuid.uuid4())[:8]}"
        category_code = f"ITC{str(uuid.uuid4())[:8]}"
        create_cat_response = await create_expense_category(
            extend=extend,
            name=category_name,
            code=category_code,
            required=True,
            active=True,
            free_text_allowed=False,
        )
        category = create_cat_response
        category_id = category["id"]

        # Create a new label for this expense category
        label_name = f"Label {str(uuid.uuid4())[:8]}"
        label_code = f"LBL{str(uuid.uuid4())[:8]}"
        create_label_response = await create_expense_category_label(
            extend=extend,
            category_id=category_id,
            name=label_name,
            code=label_code,
            active=True
        )
        label = create_label_response
        assert label, "Expense category label creation failed"
        label_id = label["id"]

        # List labels for the expense category
        list_labels_response = await get_expense_category_labels(
            extend=extend,
            category_id=category_id,
            page=0,
            per_page=10
        )
        labels = list_labels_response.get("expenseLabels")
        assert labels is not None, "Expense category labels not found in response"
        # Verify that the newly created label is present in the list
        assert any(l["id"] == label_id for l in labels), "Created label not found in list"

    @pytest.mark.asyncio
    async def test_update_expense_category_label(self, extend):
        """Test updating an expense category label"""
        # Create a new expense category first
        category_name = f"Integration Test Category {str(uuid.uuid4())[:8]}"
        category_code = f"ITC{str(uuid.uuid4())[:8]}"
        create_cat_response = await create_expense_category(
            extend=extend,
            name=category_name,
            code=category_code,
            required=True,
            active=True,
            free_text_allowed=False,
        )
        category = create_cat_response
        category_id = category["id"]

        # Create a new label for this category
        label_name = f"Label {str(uuid.uuid4())[:8]}"
        label_code = f"LBL{str(uuid.uuid4())[:8]}"
        create_label_response = await create_expense_category_label(
            extend=extend,
            category_id=category_id,
            name=label_name,
            code=label_code,
            active=True
        )
        label = create_label_response
        label_id = label["id"]

        # Update the expense category label
        new_label_name = f"Updated Label {str(uuid.uuid4())[:8]}"
        update_label_response = await update_expense_category_label(
            extend=extend,
            category_id=category_id,
            label_id=label_id,
            name=new_label_name
        )
        updated_label = update_label_response
        assert updated_label, "Expense category label update failed"
        assert updated_label["name"] == new_label_name


@pytest.mark.integration
class TestReceiptAttachments:
    """Integration tests for receipt attachment operations"""

    @pytest.mark.asyncio
    async def test_create_receipt_attachment(self, extend):
        """
        Test creating a receipt attachment for a transaction by uploading a file.
        """

        # Retrieve a transaction to attach the receipt to
        transactions_response = await get_transactions(extend, page=0, per_page=1)
        if not transactions_response.get("report", {}).get("transactions"):
            pytest.skip("No transactions available to attach receipt to")
        transaction_id = transactions_response["report"]["transactions"][0]["id"]

        # Create a temporary PNG file with minimal valid header bytes
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            # Write minimal PNG header bytes (this is not a complete image,
            # but may be sufficient for testing file upload endpoints)
            tmp.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
                      b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89')
            tmp.flush()
            tmp_name = tmp.name

        try:
            response = await create_receipt_attachment(
                extend=extend,
                transaction_id=transaction_id,
                file_path=tmp_name
            )
            # Verify that the response contains expected receipt attachment fields.
            # Adjust these assertions based on your API response structure.
            assert response is not None, "Response should not be None"

            # Check for common fields in a successful response
            for field in ["id", "transactionId", "contentType", "urls", "createdAt", "uploadType"]:
                assert field in response, f"Missing expected field: {field}"

            # Initiate an automatch job
            automatch_response = await automatch_receipts(
                extend=extend,
                receipt_attachment_ids=[response["id"]]
            )
            assert "id" in automatch_response, "Automatch response should include a job id"
            assert "tasks" in automatch_response, "Automatch response should include tasks"

            job_id = automatch_response["id"]
            # Retrieve the automatch job status using the new endpoint
            status_response = await extend.receipt_capture.get_automatch_status(job_id)
            assert "id" in status_response, "Status response should include a job id"
            assert status_response["id"] == job_id, "Job id should match the one returned during automatch"
            assert "tasks" in status_response, "Status response should include tasks"

        finally:
            # Clean up the temporary file
            os.remove(tmp_name)

    @pytest.mark.asyncio
    async def test_send_receipt_reminder(self, extend):
        """
        Test sending a receipt reminder for a transaction.
        """
        # Retrieve a transaction to send a reminder for
        transactions_response = await get_transactions(extend, page=0, per_page=10, receipt_missing=True)
        if not transactions_response.get("report", {}).get("transactions"):
            pytest.skip("No transactions available to send receipt reminder for")
        transaction_id = transactions_response["report"]["transactions"][0]["id"]

        try:
            # Send receipt reminder
            result = await send_receipt_reminder(extend, transaction_id)
            # The call should succeed and return None
            assert result is None
        except Exception as exc:
            # With exception chaining, check the cause.
            original_error = exc.__cause__
            assert original_error is not None, "Expected a chained exception"
            if isinstance(original_error, httpx.HTTPStatusError):
                assert original_error.response.status_code == 429
            else:
                raise AssertionError("Expected httpx.HTTPStatusError as the cause") from exc


def test_environment_variables():
    """Test that required environment variables are set"""
    assert os.environ.get("EXTEND_API_KEY"), "EXTEND_API_KEY environment variable is required"
    assert os.environ.get("EXTEND_API_SECRET"), "EXTEND_API_SECRET environment variable is required"
