"""Comprehensive test suite for Mechanic endpoints."""

import unittest
from tests.base import BaseAPITestCase


class TestCreateMechanic(BaseAPITestCase):
    """Test POST /mechanics/ endpoint."""

    def test_create_mechanic_success(self):
        """Positive: Create mechanic with all required fields."""
        response = self.create_mechanic()
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["email"], "bob@example.com")
        self.assertNotIn("password", data)

    def test_create_mechanic_with_unique_data(self):
        """Positive: Create mechanic with different data."""
        response = self.create_mechanic(
            name="John Smith",
            email="john@example.com",
            phone="555-1111",
            salary=60000
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "John Smith")
        self.assertEqual(data["salary"], 60000)

    def test_create_mechanic_missing_name(self):
        """Negative: Mechanic creation fails without name."""
        response = self.client.post(
            "/mechanics/",
            json={"email": "test@example.com", "phone": "555-1234", "salary": 50000, "password": "pass"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_missing_salary(self):
        """Negative: Mechanic creation fails without salary."""
        response = self.client.post(
            "/mechanics/",
            json={"name": "Test", "email": "test@example.com", "phone": "555-1234", "password": "pass"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_invalid_salary(self):
        """Negative: Mechanic creation fails with negative salary."""
        response = self.client.post(
            "/mechanics/",
            json={"name": "Test", "email": "test@example.com", "phone": "555-1234", "salary": -1000, "password": "pass"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_duplicate_email(self):
        """Negative: Mechanic creation fails with duplicate email."""
        self.create_mechanic(email="duplicate@example.com")
        response = self.client.post(
            "/mechanics/",
            json={"name": "Another", "email": "duplicate@example.com", "phone": "555-9999", "salary": 55000, "password": "pass"}
        )
        self.assertEqual(response.status_code, 400)


class TestMechanicLogin(BaseAPITestCase):
    """Test POST /mechanics/login endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()

    def test_login_success(self):
        """Positive: Successful mechanic login."""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "bob@example.com", "password": "mechpass"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["mechanic_id"], 1)

    def test_login_invalid_email(self):
        """Negative: Login fails with non-existent email."""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "nonexistent@example.com", "password": "mechpass"}
        )
        self.assertEqual(response.status_code, 401)

    def test_login_invalid_password(self):
        """Negative: Login fails with wrong password."""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "bob@example.com", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 401)

    def test_login_missing_email(self):
        """Negative: Login fails without email."""
        response = self.client.post(
            "/mechanics/login",
            json={"password": "mechpass"}
        )
        self.assertEqual(response.status_code, 400)

    def test_login_rate_limiting(self):
        """Negative: Login rate limiting (10 per minute)."""
        for i in range(11):
            response = self.client.post(
                "/mechanics/login",
                json={"email": "bob@example.com", "password": "wrongpass"}
            )
            if i < 10:
                self.assertIn(response.status_code, [401, 400])
            else:
                self.assertEqual(response.status_code, 429)


class TestGetMechanics(BaseAPITestCase):
    """Test GET /mechanics/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic(name="Bob", email="bob@example.com")
        self.create_mechanic(name="John", email="john@example.com")
        self.create_mechanic(name="Charlie", email="charlie@example.com")

    def test_get_mechanics_success(self):
        """Positive: Retrieve mechanics list."""
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 3)

    def test_get_mechanics_contains_all_fields(self):
        """Positive: Mechanics list contains required fields."""
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        mechanic = data[0]
        self.assertIn("id", mechanic)
        self.assertIn("name", mechanic)
        self.assertIn("email", mechanic)
        self.assertIn("salary", mechanic)


class TestGetMostTickets(BaseAPITestCase):
    """Test GET /mechanics/most-tickets endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()

    def test_most_tickets_success(self):
        """Positive: Retrieve mechanics sorted by ticket count."""
        response = self.client.get("/mechanics/most-tickets")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    def test_most_tickets_contains_ticket_count(self):
        """Positive: Most tickets response includes ticket_count."""
        response = self.client.get("/mechanics/most-tickets")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        mechanic = data[0]
        self.assertIn("ticket_count", mechanic)
        self.assertEqual(mechanic["ticket_count"], 0)


class TestUpdateMechanic(BaseAPITestCase):
    """Test PUT /mechanics/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.token = self.login_mechanic()

    def test_update_mechanic_success(self):
        """Positive: Update mechanic successfully."""
        response = self.client.put(
            "/mechanics/1",
            json={"phone": "555-0000"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["phone"], "555-0000")

    def test_update_mechanic_name(self):
        """Positive: Update mechanic name."""
        response = self.client.put(
            "/mechanics/1",
            json={"name": "Robert"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Robert")

    def test_update_mechanic_salary(self):
        """Positive: Update mechanic salary."""
        response = self.client.put(
            "/mechanics/1",
            json={"salary": 65000},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["salary"], 65000)

    def test_update_mechanic_unauthorized(self):
        """Negative: Update fails without authentication."""
        response = self.client.put(
            "/mechanics/1",
            json={"phone": "555-0000"}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_mechanic_not_found(self):
        """Negative: Update of non-existent mechanic."""
        response = self.client.put(
            "/mechanics/999",
            json={"phone": "555-0000"},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_mechanic_invalid_salary(self):
        """Negative: Update with invalid salary."""
        response = self.client.put(
            "/mechanics/1",
            json={"salary": -5000},
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 400)


class TestDeleteMechanic(BaseAPITestCase):
    """Test DELETE /mechanics/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.token = self.login_mechanic()

    def test_delete_mechanic_success(self):
        """Positive: Delete mechanic successfully."""
        response = self.client.delete(
            "/mechanics/1",
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_mechanic_unauthorized(self):
        """Negative: Delete fails without authentication."""
        response = self.client.delete("/mechanics/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_mechanic_not_found(self):
        """Negative: Delete of non-existent mechanic."""
        response = self.client.delete(
            "/mechanics/999",
            headers=self.auth_header(self.token)
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
