"""Swagger/OpenAPI definitions for all endpoints."""

definitions = {
    "Customer": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "name": {"type": "string", "example": "Alice Johnson"},
            "email": {"type": "string", "example": "alice@example.com"},
            "phone": {"type": "string", "example": "555-1234"},
        },
        "required": ["id", "name", "email", "phone"],
    },
    "CustomerPayload": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "Alice Johnson"},
            "email": {"type": "string", "example": "alice@example.com"},
            "phone": {"type": "string", "example": "555-1234"},
            "password": {"type": "string", "example": "secret123"},
        },
        "required": ["name", "email", "phone", "password"],
    },
    "CustomerUpdatePayload": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "Alice Johnson"},
            "email": {"type": "string", "example": "alice@example.com"},
            "phone": {"type": "string", "example": "555-1234"},
            "password": {"type": "string", "example": "newsecret456"},
        },
    },
    "Login": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "example": "alice@example.com"},
            "password": {"type": "string", "example": "secret123"},
        },
        "required": ["email", "password"],
    },
    "Mechanic": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "name": {"type": "string", "example": "Bob Smith"},
            "email": {"type": "string", "example": "bob@example.com"},
            "phone": {"type": "string", "example": "555-5678"},
            "salary": {"type": "number", "format": "float", "example": 55000.0},
        },
        "required": ["id", "name", "email", "phone", "salary"],
    },
    "MechanicPayload": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "Bob Smith"},
            "email": {"type": "string", "example": "bob@example.com"},
            "phone": {"type": "string", "example": "555-5678"},
            "salary": {"type": "number", "format": "float", "example": 55000.0},
            "password": {"type": "string", "example": "mechpass"},
        },
        "required": ["name", "email", "phone", "salary", "password"],
    },
    "MechanicUpdatePayload": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "Bob Smith"},
            "email": {"type": "string", "example": "bob@example.com"},
            "phone": {"type": "string", "example": "555-5678"},
            "salary": {"type": "number", "format": "float", "example": 55000.0},
            "password": {"type": "string", "example": "newmechpass"},
        },
    },
    "ServiceTicket": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "vin": {"type": "string", "example": "1HGCM82633A004352"},
            "service_date": {"type": "string", "format": "date", "example": "2026-07-28"},
            "service_desc": {"type": "string", "example": "Oil change and filter replacement"},
            "customer_id": {"type": "integer", "example": 1},
            "mechanics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Bob Smith"},
                        "email": {"type": "string", "example": "bob@example.com"},
                    },
                },
            },
            "parts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Oil Filter"},
                        "price": {"type": "number", "format": "float", "example": 9.99},
                    },
                },
            },
        },
        "required": ["id", "vin", "service_date", "service_desc", "customer_id"],
    },
    "ServiceTicketPayload": {
        "type": "object",
        "properties": {
            "vin": {"type": "string", "example": "1HGCM82633A004352"},
            "service_date": {"type": "string", "format": "date", "example": "2026-07-28"},
            "service_desc": {"type": "string", "example": "Oil change and filter replacement"},
            "customer_id": {"type": "integer", "example": 1},
        },
        "required": ["vin", "service_date", "service_desc", "customer_id"],
    },
    "EditTicketPayload": {
        "type": "object",
        "properties": {
            "add_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "example": [1, 2],
                "description": "Mechanic IDs to assign to ticket",
            },
            "remove_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "example": [3],
                "description": "Mechanic IDs to remove from ticket",
            },
        },
    },
    "AddPartPayload": {
        "type": "object",
        "properties": {
            "inventory_id": {"type": "integer", "example": 1},
            "quantity": {"type": "integer", "example": 2, "default": 1},
        },
        "required": ["inventory_id"],
    },
    "Inventory": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "example": 1},
            "name": {"type": "string", "example": "Oil Filter"},
            "price": {"type": "number", "format": "float", "example": 9.99},
        },
        "required": ["id", "name", "price"],
    },
    "InventoryPayload": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "example": "Oil Filter"},
            "price": {"type": "number", "format": "float", "example": 9.99},
        },
        "required": ["name", "price"],
    },
}

# Flasgger config removed - using defaults

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic Shop API v4",
        "description": "A comprehensive REST API for managing a mechanic shop with customers, mechanics, service tickets, and inventory. Features JWT authentication, rate limiting, caching, and comprehensive documentation with full test coverage.",
        "contact": {
            "email": "api@mechanicshop.local",
        },
        "version": "4.0.0",
    },
    "host": "mechanic-shop-api-o2l5.onrender.com",
    "basePath": "/",
    "schemes": ["https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'",
        }
    },
    "definitions": definitions,
}
