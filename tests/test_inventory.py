"""Comprehensive test suite for Inventory endpoints."""

import unittest
from tests.base import BaseAPITestCase


class TestCreatePart(BaseAPITestCase):
    """Test POST /inventory/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()

    def test_create_part_success(self):
        """Positive: Create inventory part with all required fields."""
        response = self.create_part(self.mechanic_token)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Oil Filter")
        self.assertEqual(data["price"], 9.99)

    def test_create_part_with_custom_data(self):
        """Positive: Create part with custom name and price."""
        response = self.client.post(
            "/inventory/",
            json={"name": "Spark Plug", "price": 15.99},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Spark Plug")
        self.assertEqual(data["price"], 15.99)

    def test_create_part_unauthorized(self):
        """Negative: Creation fails without authentication."""
        response = self.client.post(
            "/inventory/",
            json={"name": "Oil Filter", "price": 9.99}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_part_missing_name(self):
        """Negative: Creation fails without name."""
        response = self.client.post(
            "/inventory/",
            json={"price": 9.99},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_part_missing_price(self):
        """Negative: Creation fails without price."""
        response = self.client.post(
            "/inventory/",
            json={"name": "Oil Filter"},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_part_negative_price(self):
        """Negative: Creation fails with negative price."""
        response = self.client.post(
            "/inventory/",
            json={"name": "Oil Filter", "price": -5.0},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_create_part_zero_price(self):
        """Negative: Creation fails with zero price."""
        response = self.client.post(
            "/inventory/",
            json={"name": "Oil Filter", "price": 0},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)


class TestGetParts(BaseAPITestCase):
    """Test GET /inventory/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_part(self.mechanic_token)
        self.client.post(
            "/inventory/",
            json={"name": "Spark Plug", "price": 15.99},
            headers=self.auth_header(self.mechanic_token)
        )

    def test_get_parts_success(self):
        """Positive: Retrieve inventory parts list."""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_get_parts_contains_all_fields(self):
        """Positive: Parts list contains required fields."""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        part = data[0]
        self.assertIn("id", part)
        self.assertIn("name", part)
        self.assertIn("price", part)

    def test_get_parts_empty_list(self):
        """Positive: Retrieve empty parts list."""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)


class TestGetPartById(BaseAPITestCase):
    """Test GET /inventory/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_part(self.mechanic_token)

    def test_get_part_success(self):
        """Positive: Retrieve part by ID."""
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Oil Filter")
        self.assertEqual(data["price"], 9.99)

    def test_get_part_not_found(self):
        """Negative: Retrieve non-existent part."""
        response = self.client.get("/inventory/999")
        self.assertEqual(response.status_code, 404)

    def test_get_part_invalid_id(self):
        """Negative: Retrieve with invalid ID format."""
        response = self.client.get("/inventory/invalid")
        self.assertEqual(response.status_code, 404)


class TestUpdatePart(BaseAPITestCase):
    """Test PUT /inventory/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_part(self.mechanic_token)

    def test_update_part_price(self):
        """Positive: Update part price."""
        response = self.client.put(
            "/inventory/1",
            json={"price": 12.5},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["price"], 12.5)

    def test_update_part_name(self):
        """Positive: Update part name."""
        response = self.client.put(
            "/inventory/1",
            json={"name": "Premium Oil Filter"},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Premium Oil Filter")

    def test_update_part_unauthorized(self):
        """Negative: Update fails without authentication."""
        response = self.client.put(
            "/inventory/1",
            json={"price": 12.5}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_part_not_found(self):
        """Negative: Update fails for non-existent part."""
        response = self.client.put(
            "/inventory/999",
            json={"price": 12.5},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_update_part_negative_price(self):
        """Negative: Update fails with negative price."""
        response = self.client.put(
            "/inventory/1",
            json={"price": -10},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)


class TestDeletePart(BaseAPITestCase):
    """Test DELETE /inventory/<id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_part(self.mechanic_token)

    def test_delete_part_success(self):
        """Positive: Delete part successfully."""
        response = self.client.delete(
            "/inventory/1",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_part_unauthorized(self):
        """Negative: Delete fails without authentication."""
        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 401)

    def test_delete_part_not_found(self):
        """Negative: Delete fails for non-existent part."""
        response = self.client.delete(
            "/inventory/999",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_part_verify_deletion(self):
        """Positive: Verify part is deleted."""
        self.client.delete(
            "/inventory/1",
            headers=self.auth_header(self.mechanic_token)
        )
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()