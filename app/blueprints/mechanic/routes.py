from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import func

from app.extensions import db, limiter, cache
from app.models import Mechanic, service_mechanics
from app.blueprints.mechanic import mechanic_bp
from app.blueprints.mechanic.schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from app.utils import encode_mechanic_token, mechanic_token_required


@mechanic_bp.route("/", methods=["POST"])
def create_mechanic():
    """
    Create a new mechanic
    ---
    tags:
      - Mechanics
    summary: Create a new mechanic
    description: Register a new mechanic with name, email, phone, salary, and password.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicPayload'
    responses:
      201:
        description: Mechanic created successfully
        schema:
          $ref: '#/definitions/Mechanic'
      400:
        description: Validation error
    """
    try:
        mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    mechanic.set_password(mechanic.password)
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201


@mechanic_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """
    Mechanic login
    ---
    tags:
      - Mechanics
    summary: Log in as a mechanic
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
            mechanic_id:
              type: integer
              example: 1
      401:
        description: Invalid email or password
    """
    try:
        credentials = mechanic_login_schema.load(request.json, partial=True, transient=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    mechanic = Mechanic.query.filter_by(email=credentials.email).first()
    if not mechanic or not mechanic.check_password(credentials.password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_mechanic_token(mechanic.id)
    return jsonify({"token": token, "mechanic_id": mechanic.id}), 200


@mechanic_bp.route("/", methods=["GET"])
def get_mechanics():
    """
    List all mechanics
    ---
    tags:
      - Mechanics
    summary: Retrieve all mechanics
    description: Fetch a list of all mechanics in the system.
    responses:
      200:
        description: List of mechanics
        schema:
          type: array
          items:
            $ref: '#/definitions/Mechanic'
    """
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanic_bp.route("/most-tickets", methods=["GET"])
@cache.cached(timeout=60)
def mechanics_by_ticket_count():
    """
    Get mechanics ranked by ticket count
    ---
    tags:
      - Mechanics
    summary: List mechanics ranked by number of service tickets
    description: Returns all mechanics sorted by the number of service tickets they are assigned to (cached for 60 seconds).
    responses:
      200:
        description: List of mechanics with ticket_count field
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Bob Smith"
              email:
                type: string
                example: "bob@example.com"
              phone:
                type: string
                example: "555-5678"
              salary:
                type: number
                example: 55000.0
              ticket_count:
                type: integer
                example: 5
    """
    results = (
        db.session.query(Mechanic, func.count(service_mechanics.c.service_ticket_id).label("ticket_count"))
        .outerjoin(service_mechanics, Mechanic.id == service_mechanics.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(service_mechanics.c.service_ticket_id).desc())
        .all()
    )

    data = []
    for mechanic, ticket_count in results:
        entry = mechanic_schema.dump(mechanic)
        entry["ticket_count"] = ticket_count
        data.append(entry)

    return jsonify(data), 200


@mechanic_bp.route("/<int:id>", methods=["PUT"])
@mechanic_token_required
def update_mechanic(mechanic_id, id):
    """
    Update mechanic profile
    ---
    tags:
      - Mechanics
    summary: Update a mechanic's information
    description: Update mechanic details (name, email, phone, salary, password).
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Mechanic ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/MechanicUpdatePayload'
    responses:
      200:
        description: Mechanic updated successfully
        schema:
          $ref: '#/definitions/Mechanic'
      400:
        description: Validation error
      401:
        description: Missing or invalid token
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        mechanic = mechanic_schema.load(request.json, instance=mechanic, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "password" in (request.json or {}):
        mechanic.set_password(mechanic.password)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanic_bp.route("/<int:id>", methods=["DELETE"])
@mechanic_token_required
def delete_mechanic(mechanic_id, id):
    """
    Delete a mechanic
    ---
    tags:
      - Mechanics
    summary: Delete a mechanic
    description: Remove a mechanic from the system. Does not cascade-delete assigned tickets.
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Mechanic ID
    responses:
      200:
        description: Mechanic deleted successfully
      401:
        description: Missing or invalid token
      404:
        description: Mechanic not found
    """
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id {id} successfully deleted"}), 200
