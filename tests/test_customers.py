"""Comprehensive test suite for Customer endpoints."""

import unittest
from tests.base import BaseAPITestCase


class TestCreateCustomer(BaseAPITestCase):
    """Test POST /customers/ endpoint."""

    def test_create_customer_success(self):
        """Positive: Create customer with all required fields."""
        response = self.create_customer()
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Alice")
        self.assertEqual(data["email"], "alice@example.com")
        self.assertNotIn("password", data)

    def test_create_customer_with_unique_data(self):
        """Positive: Create customer with different data."""
        response = self.create_customer(
            name="Bob Johnson",
            email="bob@example.com",
            phone="555-5678",
            password="pass123"
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Bob Johnson")
        self.assertEqual(data["phone"], "555-5678")

    def test_create_customer_missing_name(self):
        """Negative: Customer creation fails without name."""
        response = self.client.post(
            "/customers/",
            json={"email": "test@example.com", "phone": "555-1234", "password": "secret"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_customer_missing_email(self):
        """Negative: Customer creation fails without email."""
        response = self.client.post(
            "/customers/",
            json={"name": "Test", "phone": "555-1234", "password": "secret"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_customer_missing_phone(self):
        """Negative: Customer creation fails without phone."""
        response = self.client.post(
            "/customers/",
            json={"name": "Test", "email": "test@example.com", "password": "secret"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_customer_missing_password(self):
        """Negative: Customer creation fails without password."""
        response = self.client.post(
            "/customers/",
            json={"name": "Test", "email": "test@example.com", "phone": "555-1234"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_customer_invalid_email(self):
        """Negative: Customer creation fails with invalid email."""
        response = self.client.post(
            "/customers/",
            json={"name": "Test", "email": "invalid-email", "phone": "555-1234", "password": "secret"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_customer_duplicate_email(self):
        """Negative: Customer creation fails with duplicate email."""
        self.create_customer(email="duplicate@example.com")
        response = self.client.post(
            "/customers/",
            json={"name": "Another", "email": "duplicate@example.com", "phone": "555-9999", "password": "secret"}
        )
        self.assertEqual(response.status_code, 400)


class TestCustomerLogin(BaseAPITestCase):
    """Test POST /customers/login endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()

    def test_login_success(self):
        """Positive: Successful customer login."""
        response = self.client.post(
            "/customers/login",
            json={"email": "alice@example.com", "password": "secret123"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["customer_id"], 1)

    def test_login_invalid_email(self):
        """Negative: Login fails with non-existent email."""
        response = self.client.post(
            "/customers/login",
            json={"email": "nonexistent@example.com", "password": "secret123"}
        )
        self.assertEqual(response.status_code, 401)

    def test_login_invalid_password(self):
        """Negative: Login fails with wrong password."""
        response = self.client.post(
            "/customers/login",
            json={"email": "alice@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)

    def test_login_missing_email(self):
        """Negative: Login fails without email."""
        response = self.client.post(
            "/customers/login",
            json={"password": "secret123"}
        )
        self.assertEqual(response.status_code, 400)

    def test_login_missing_password(self):
        """Negative: Login fails without password."""
        response = self.client.post(
            "/customers/login",
            json={"email": "alice@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_login_rate_limiting(self):
        """Negative: Login rate limiting (10 per minute)."""
        for i in range(11):
            response = self.client.post(
                "/customers/login",
                json={"email": "alice@example.com", "password": "wrongpassword"}
            )
            if i < 10:
                self.assertIn(response.status_code, [401, 400])
            else:
                self.assertEqual(response.status_code, 429)


class TestGetCustomers(BaseAPITestCase):
    """Test GET /customers/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer(name="Alice", email="alice@example.com")
        self.create_customer(name="Bob", email="bob@example.com", phone="555-5678")
        self.create_customer(name="Charlie", email="charlie@example.com", phone="555-9999")

    def test_get_customers_success(self):
        """Positive: Retrieve customers list."""
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("customers", data)
        self.assertEqual(len(data["customers"]), 3)
        self.assertEqual(data["total"], 3)

    def test_get_customers_pagination_page_1(self):
        """Positive: Pagination with page 1."""
        response = self.client.get("/customers/?page=1&per_page=2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["customers"]), 2)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["total_pages"], 2)

    def test_get_customers_pagination_page_2(self):
        """Positive: Pagination with page 2."""
        response = self.client.get("/customers/?page=2&per_page=2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["customers"]), 1)

    def test_get_customers_invalid_page(self):
        """Negative: Pagination with invalid page number."""
        response = self.client.get("/customers/?page=-1")
        self.assertEqual(response.status_code, 200)


class TestGetCustomerById(BaseAPITestCase):
    """Test GET /customers/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()

    def test_get_customer_success(self):
        """Positive: Retrieve customer by ID."""
        response = self.client.get("/customers/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["email"], "alice@example.com")

    def test_get_customer_not_found(self):
        """Negative: Retrieve non-existent customer."""
        response = self.client.get("/customers/999")
        self.assertEqual(response.status_code, 404)


class TestUpdateCustomer(BaseAPITestCase):
    """Test PUT /customers/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.token = self.login_customer()

    def test_update_customer_success(self):
        """Positive: Update customer successfully."""
        response = self.client.put(
            "/customers/1",
            json={"name": "Alice Updated", "phone": "555-9999"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Alice Updated")
        self.assertEqual(data["phone"], "555-9999")

    def test_update_customer_password(self):
        """Positive: Update customer password."""
        response = self.client.put(
            "/customers/1",
            json={"password": "newpassword123"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_customer_email(self):
        """Positive: Update customer email."""
        response = self.client.put(
            "/customers/1",
            json={"email": "newemail@example.com"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)

    def test_update_customer_unauthorized(self):
        """Negative: Update fails without authentication."""
        response = self.client.put(
            "/customers/1",
            json={"name": "Hacker"}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_another_customer_forbidden(self):
        """Negative: Customer cannot update another customer."""
        self.create_customer(name="Bob", email="bob@example.com", phone="555-5678")
        response = self.client.put(
            "/customers/2",
            json={"name": "Hacked"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 403)

    def test_update_customer_invalid_email(self):
        """Negative: Update with invalid email format."""
        response = self.client.put(
            "/customers/1",
            json={"email": "invalid-email"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 400)


class TestDeleteCustomer(BaseAPITestCase):
    """Test DELETE /customers/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.token = self.login_customer()

    def test_delete_customer_success(self):
        """Positive: Delete customer successfully."""
        response = self.client.delete(
            "/customers/1",
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_customer_unauthorized(self):
        """Negative: Delete fails without authentication."""
        response = self.client.delete("/customers/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_another_customer_forbidden(self):
        """Negative: Customer cannot delete another customer."""
        self.create_customer(name="Bob", email="bob@example.com", phone="555-5678")
        response = self.client.delete(
            "/customers/2",
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 403)


class TestGetMyTickets(BaseAPITestCase):
    """Test GET /customers/my-tickets endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.token = self.login_customer()
        self.create_service_ticket(customer_id=1, vin="1HGCM82633A004352")
        self.create_service_ticket(customer_id=1, vin="2HGCM82633A004353")

    def test_get_my_tickets_success(self):
        """Positive: Retrieve customer's service tickets."""
        response = self.client.get(
            "/customers/my-tickets",
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_get_my_tickets_unauthorized(self):
        """Negative: Retrieval fails without authentication."""
        response = self.client.get("/customers/my-tickets")
        self.assertEqual(response.status_code, 401)

    def test_get_my_tickets_empty(self):
        """Positive: Retrieval when customer has no tickets."""
        self.create_customer(name="NoTickets", email="no@example.com", phone="555-0000")
        token = self.login_customer(email="no@example.com", password="secret123")
        response = self.client.get(
            "/customers/my-tickets",
            headers=self.auth_header(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_get_my_tickets_invalid_token(self):
        """Negative: Retrieval with invalid token."""
        response = self.client.get(
            "/customers/my-tickets",
            headers=self.auth_header("invalid.token.here")
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
