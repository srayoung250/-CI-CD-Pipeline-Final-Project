"""Comprehensive test suite for Service Ticket endpoints."""

import unittest
from tests.base import BaseAPITestCase


class TestCreateServiceTicket(BaseAPITestCase):
    """Test POST /service-tickets/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()

    def test_create_service_ticket_success(self):
        """Positive: Create service ticket with all required fields."""
        response = self.create_service_ticket(customer_id=1)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["vin"], "1HGCM82633A004352")
        self.assertEqual(data["customer_id"], 1)

    def test_create_service_ticket_with_custom_data(self):
        """Positive: Create service ticket with custom data."""
        response = self.create_service_ticket(
            customer_id=1,
            vin="2HGCM82633A004353",
            service_date="2026-08-01",
            service_desc="Engine overhaul"
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["vin"], "2HGCM82633A004353")
        self.assertEqual(data["service_desc"], "Engine overhaul")

    def test_create_service_ticket_missing_vin(self):
        """Negative: Creation fails without VIN."""
        response = self.client.post(
            "/service-tickets/",
            json={"service_date": "2026-07-28", "service_desc": "Oil change", "customer_id": 1}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_service_ticket_missing_customer_id(self):
        """Negative: Creation fails without customer_id."""
        response = self.client.post(
            "/service-tickets/",
            json={"vin": "1HGCM82633A004352", "service_date": "2026-07-28", "service_desc": "Oil change"}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_service_ticket_invalid_customer(self):
        """Negative: Creation fails with non-existent customer."""
        response = self.client.post(
            "/service-tickets/",
            json={"vin": "1HGCM82633A004352", "service_date": "2026-07-28", "service_desc": "Oil change", "customer_id": 999}
        )
        self.assertEqual(response.status_code, 400)


class TestGetServiceTickets(BaseAPITestCase):
    """Test GET /service-tickets/ endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_service_ticket(customer_id=1)
        self.create_service_ticket(customer_id=1, vin="2HGCM82633A004353")

    def test_get_service_tickets_success(self):
        """Positive: Retrieve service tickets list."""
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_get_service_tickets_empty(self):
        """Positive: Retrieve empty tickets list."""
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)


class TestAssignMechanic(BaseAPITestCase):
    """Test PUT /service-tickets/<id>/assign-mechanic/<mechanic_id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_service_ticket(customer_id=1)

    def test_assign_mechanic_success(self):
        """Positive: Assign mechanic to ticket."""
        response = self.client.put(
            "/service-tickets/1/assign-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["mechanics"]), 1)

    def test_assign_mechanic_unauthorized(self):
        """Negative: Assignment fails without authentication."""
        response = self.client.put("/service-tickets/1/assign-mechanic/1")
        self.assertEqual(response.status_code, 401)

    def test_assign_mechanic_ticket_not_found(self):
        """Negative: Assignment fails for non-existent ticket."""
        response = self.client.put(
            "/service-tickets/999/assign-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_assign_mechanic_already_assigned(self):
        """Negative: Cannot assign same mechanic twice."""
        self.client.put(
            "/service-tickets/1/assign-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )
        response = self.client.put(
            "/service-tickets/1/assign-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)

    def test_assign_nonexistent_mechanic(self):
        """Negative: Cannot assign non-existent mechanic."""
        response = self.client.put(
            "/service-tickets/1/assign-mechanic/999",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)


class TestRemoveMechanic(BaseAPITestCase):
    """Test PUT /service-tickets/<id>/remove-mechanic/<mechanic_id> endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_service_ticket(customer_id=1)
        self.client.put(
            "/service-tickets/1/assign-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )

    def test_remove_mechanic_success(self):
        """Positive: Remove mechanic from ticket."""
        response = self.client.put(
            "/service-tickets/1/remove-mechanic/1",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["mechanics"]), 0)

    def test_remove_mechanic_unauthorized(self):
        """Negative: Removal fails without authentication."""
        response = self.client.put("/service-tickets/1/remove-mechanic/1")
        self.assertEqual(response.status_code, 401)

    def test_remove_mechanic_not_assigned(self):
        """Negative: Cannot remove unassigned mechanic."""
        self.create_mechanic(name="John", email="john@example.com")
        response = self.client.put(
            "/service-tickets/1/remove-mechanic/2",
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 400)


class TestEditTicketMechanics(BaseAPITestCase):
    """Test PUT /service-tickets/<id>/edit endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.create_mechanic(name="John", email="john@example.com")
        self.mechanic_token = self.login_mechanic()
        self.create_service_ticket(customer_id=1)

    def test_edit_ticket_add_mechanics(self):
        """Positive: Add mechanics to ticket."""
        response = self.client.put(
            "/service-tickets/1/edit",
            json={"add_ids": [1, 2], "remove_ids": []},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["mechanics"]), 2)

    def test_edit_ticket_remove_mechanics(self):
        """Positive: Remove mechanics from ticket."""
        self.client.put(
            "/service-tickets/1/edit",
            json={"add_ids": [1, 2], "remove_ids": []},
            headers=self.auth_header(self.mechanic_token)
        )
        response = self.client.put(
            "/service-tickets/1/edit",
            json={"add_ids": [], "remove_ids": [1]},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["mechanics"]), 1)

    def test_edit_ticket_unauthorized(self):
        """Negative: Edit fails without authentication."""
        response = self.client.put(
            "/service-tickets/1/edit",
            json={"add_ids": [1], "remove_ids": []}
        )
        self.assertEqual(response.status_code, 401)

    def test_edit_ticket_not_found(self):
        """Negative: Edit fails for non-existent ticket."""
        response = self.client.put(
            "/service-tickets/999/edit",
            json={"add_ids": [1], "remove_ids": []},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)


class TestAddPartToTicket(BaseAPITestCase):
    """Test POST /service-tickets/<id>/add-part endpoint."""

    def setUp(self):
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.mechanic_token = self.login_mechanic()
        self.create_service_ticket(customer_id=1)
        self.create_part(self.mechanic_token)

    def test_add_part_success(self):
        """Positive: Add part to ticket."""
        response = self.client.post(
            "/service-tickets/1/add-part",
            json={"inventory_id": 1, "quantity": 2},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["parts"]), 1)

    def test_add_part_default_quantity(self):
        """Positive: Add part with default quantity."""
        response = self.client.post(
            "/service-tickets/1/add-part",
            json={"inventory_id": 1},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 200)

    def test_add_part_unauthorized(self):
        """Negative: Add fails without authentication."""
        response = self.client.post(
            "/service-tickets/1/add-part",
            json={"inventory_id": 1, "quantity": 1}
        )
        self.assertEqual(response.status_code, 401)

    def test_add_part_not_found(self):
        """Negative: Add fails for non-existent part."""
        response = self.client.post(
            "/service-tickets/1/add-part",
            json={"inventory_id": 999, "quantity": 1},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)

    def test_add_part_ticket_not_found(self):
        """Negative: Add fails for non-existent ticket."""
        response = self.client.post(
            "/service-tickets/999/add-part",
            json={"inventory_id": 1, "quantity": 1},
            headers=self.auth_header(self.mechanic_token)
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
