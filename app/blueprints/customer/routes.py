from flask import request, jsonify
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.models import Customer, ServiceTicket
from app.blueprints.customer import customer_bp
from app.blueprints.customer.schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_ticket.schemas import service_tickets_schema
from app.utils import encode_token, token_required


@customer_bp.route("/", methods=["POST"])
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    summary: Create a new customer
    description: Register a new customer with name, email, phone, and password.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerPayload'
    responses:
      201:
        description: Customer created successfully
        schema:
          $ref: '#/definitions/Customer'
      400:
        description: Validation error
    """
    try:
        customer = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer.set_password(customer.password)
    db.session.add(customer)
    db.session.commit()
    return customer_schema.jsonify(customer), 201


@customer_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """
    Customer login
    ---
    tags:
      - Customers
    summary: Log in as a customer
    description: Authenticate with email and password to receive a JWT token (rate limited to 10 per minute).
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Login'
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
              example: "eyJ0eXAiOiJKV1QiLCJhbGc..."
            customer_id:
              type: integer
              example: 1
      401:
        description: Invalid email or password
    """
    try:
        credentials = login_schema.load(request.json, partial=True, transient=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = Customer.query.filter_by(email=credentials.email).first()
    if not customer or not customer.check_password(credentials.password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token, "customer_id": customer.id}), 200


@customer_bp.route("/my-tickets", methods=["GET"])
@token_required
def my_tickets(customer_id):
    """
    Get authenticated customer's service tickets
    ---
    tags:
      - Customers
    summary: Retrieve service tickets for the authenticated customer
    description: Returns all service tickets belonging to the logged-in customer.
    security:
      - bearer: []
    responses:
      200:
        description: List of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicket'
      401:
        description: Missing or invalid token
    """
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200


@customer_bp.route("/", methods=["GET"])
def get_customers():
    """
    List all customers (paginated)
    ---
    tags:
      - Customers
    summary: Retrieve a paginated list of customers
    description: Fetch all customers with pagination support.
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number (1-based)
      - in: query
        name: per_page
        type: integer
        default: 10
        description: Number of customers per page
    responses:
      200:
        description: Paginated list of customers
        schema:
          type: object
          properties:
            customers:
              type: array
              items:
                $ref: '#/definitions/Customer'
            page:
              type: integer
            per_page:
              type: integer
            total:
              type: integer
            total_pages:
              type: integer
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "customers": customers_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "total_pages": pagination.pages,
        }
    ), 200


@customer_bp.route("/<int:id>", methods=["GET"])
def get_customer(id):
    """
    Get a customer by ID
    ---
    tags:
      - Customers
    summary: Retrieve a specific customer
    description: Fetch details for a single customer by ID.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Customer ID
    responses:
      200:
        description: Customer details
        schema:
          $ref: '#/definitions/Customer'
      404:
        description: Customer not found
    """
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return customer_schema.jsonify(customer), 200


@customer_bp.route("/<int:id>", methods=["PUT"])
@token_required
def update_customer(customer_id, id):
    """
    Update customer profile
    ---
    tags:
      - Customers
    summary: Update a customer's information
    description: Customers can only update their own profile. Provide fields to update (name, email, phone, password).
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Customer ID (must match authenticated customer)
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CustomerUpdatePayload'
    responses:
      200:
        description: Customer updated successfully
        schema:
          $ref: '#/definitions/Customer'
      400:
        description: Validation error
      403:
        description: Cannot update another customer's profile
      404:
        description: Customer not found
    """
    if customer_id != id:
        return jsonify({"error": "You may only update your own account"}), 403

    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer = customer_schema.load(request.json, instance=customer, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "password" in (request.json or {}):
        customer.set_password(customer.password)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customer_bp.route("/<int:id>", methods=["DELETE"])
@token_required
def delete_customer(customer_id, id):
    """
    Delete a customer
    ---
    tags:
      - Customers
    summary: Delete a customer account
    description: Customers can only delete their own account. Cascades to delete associated service tickets.
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Customer ID (must match authenticated customer)
    responses:
      200:
        description: Customer deleted successfully
      403:
        description: Cannot delete another customer's account
      404:
        description: Customer not found
    """
    if customer_id != id:
        return jsonify({"error": "You may only delete your own account"}), 403

    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer id {id} successfully deleted"}), 200
