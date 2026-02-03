import pytest
from pydantic import ValidationError

from app.schemas.user import RegisterUserRequest
from app.schemas.item import CreateItemRequest


class TestUserValidation:
    def test_email_normalization(self):
        user = RegisterUserRequest(
            email="  TEST@EXAMPLE.COM  ",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"

    def test_invalid_email_rejected(self):
        with pytest.raises(ValidationError):
            RegisterUserRequest(
                email="not-an-email",
                password="testpass123",
                first_name="Test",
                last_name="User",
            )

    def test_short_password_rejected(self):
        with pytest.raises(ValidationError):
            RegisterUserRequest(
                email="test@example.com",
                password="short",
                first_name="Test",
                last_name="User",
            )


class TestItemValidation:
    def test_valid_item(self):
        item = CreateItemRequest(
            name="Test Item",
            description="A description",
            category="electronics",
            status="active",
        )
        assert item.name == "Test Item"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            CreateItemRequest(
                name="",
                description="A description",
                category="electronics",
                status="active",
            )
