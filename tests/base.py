import unittest

from app import create_app
from app.extensions import db
from config import TestingConfig


class BaseAPITestCase(unittest.TestCase):
    """Shared Flask test-client/app-context setup for all blueprint test cases."""

    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_customer(self, name="Alice", email="alice@example.com", phone="555-1234", password="secret123"):
        return self.client.post(
            "/customers/",
            json={"name": name, "email": email, "phone": phone, "password": password},
        )

    def login_customer(self, email="alice@example.com", password="secret123"):
        resp = self.client.post("/customers/login", json={"email": email, "password": password})
        return resp.get_json()["token"]

    def create_mechanic(self, name="Bob", email="bob@example.com", phone="555-5678", salary=55000, password="mechpass"):
        return self.client.post(
            "/mechanics/",
            json={"name": name, "email": email, "phone": phone, "salary": salary, "password": password},
        )

    def login_mechanic(self, email="bob@example.com", password="mechpass"):
        resp = self.client.post("/mechanics/login", json={"email": email, "password": password})
        return resp.get_json()["token"]

    def create_service_ticket(self, customer_id, vin="1HGCM82633A004352", service_date="2026-07-28", service_desc="Oil change"):
        return self.client.post(
            "/service-tickets/",
            json={
                "vin": vin,
                "service_date": service_date,
                "service_desc": service_desc,
                "customer_id": customer_id,
            },
        )

    def create_part(self, mechanic_token, name="Oil Filter", price=9.99):
        return self.client.post(
            "/inventory/",
            json={"name": name, "price": price},
            headers=self.auth_header(mechanic_token),
        )

    @staticmethod
    def auth_header(token):
        return {"Authorization": f"Bearer {token}"}
