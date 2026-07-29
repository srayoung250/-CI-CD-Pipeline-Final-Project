from flask import request, jsonify
from marshmallow import ValidationError

from app.extensions import db, cache
from app.models import Inventory
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.utils import mechanic_token_required


@inventory_bp.route("/", methods=["POST"])
@mechanic_token_required
def create_part(mechanic_id):
    """
    Create a new inventory part
    ---
    tags:
      - Inventory
    summary: Create a new part in inventory
    description: Add a new part/component to the inventory with name and price.
    security:
      - bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryPayload'
    responses:
      201:
        description: Part created successfully
        schema:
          $ref: '#/definitions/Inventory'
      400:
        description: Validation error
      401:
        description: Missing or invalid token
    """
    try:
        part = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def get_parts():
    """
    List all inventory parts
    ---
    tags:
      - Inventory
    summary: Retrieve all parts in inventory
    description: Fetch a list of all available parts (cached for 60 seconds).
    responses:
      200:
        description: List of inventory parts
        schema:
          type: array
          items:
            $ref: '#/definitions/Inventory'
    """
    parts = Inventory.query.all()
    return inventories_schema.jsonify(parts), 200


@inventory_bp.route("/<int:id>", methods=["GET"])
def get_part(id):
    """
    Get a specific inventory part
    ---
    tags:
      - Inventory
    summary: Retrieve a part by ID
    description: Fetch details for a single inventory part.
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Part ID
    responses:
      200:
        description: Part details
        schema:
          $ref: '#/definitions/Inventory'
      404:
        description: Part not found
    """
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404
    return inventory_schema.jsonify(part), 200


@inventory_bp.route("/<int:id>", methods=["PUT"])
@mechanic_token_required
def update_part(mechanic_id, id):
    """
    Update an inventory part
    ---
    tags:
      - Inventory
    summary: Update part details
    description: Update name and/or price for an inventory part.
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Part ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/InventoryPayload'
    responses:
      200:
        description: Part updated successfully
        schema:
          $ref: '#/definitions/Inventory'
      400:
        description: Validation error
      401:
        description: Missing or invalid token
      404:
        description: Part not found
    """
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    try:
        part = inventory_schema.load(request.json, instance=part, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.commit()
    return inventory_schema.jsonify(part), 200


@inventory_bp.route("/<int:id>", methods=["DELETE"])
@mechanic_token_required
def delete_part(mechanic_id, id):
    """
    Delete an inventory part
    ---
    tags:
      - Inventory
    summary: Delete a part from inventory
    description: Remove a part from inventory. Cascades to remove from any service tickets.
    security:
      - bearer: []
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: Part ID
    responses:
      200:
        description: Part deleted successfully
      401:
        description: Missing or invalid token
      404:
        description: Part not found
    """
    part = db.session.get(Inventory, id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part id {id} successfully deleted"}), 200
