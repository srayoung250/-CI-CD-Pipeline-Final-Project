from flask import request, jsonify
from marshmallow import ValidationError

from app.extensions import db
from app.models import ServiceTicket, Mechanic, Inventory, TicketInventory
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schemas import service_ticket_schema, service_tickets_schema
from app.utils import mechanic_token_required


@service_ticket_bp.route("/", methods=["POST"])
def create_service_ticket():
    """
    Create a new service ticket
    ---
    tags:
      - Service Tickets
    summary: Create a new service ticket
    description: Create a service ticket for a customer with vehicle VIN, service date, description, and customer ID.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ServiceTicketPayload'
    responses:
      201:
        description: Service ticket created successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Validation error
    """
    try:
        ticket = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201


@service_ticket_bp.route("/", methods=["GET"])
def get_service_tickets():
    """
    List all service tickets
    ---
    tags:
      - Service Tickets
    summary: Retrieve all service tickets
    description: Fetch a list of all service tickets in the system.
    responses:
      200:
        description: List of service tickets
        schema:
          type: array
          items:
            $ref: '#/definitions/ServiceTicket'
    """
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
@mechanic_token_required
def assign_mechanic(current_mechanic_id, ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket
    ---
    tags:
      - Service Tickets
    summary: Assign a mechanic to a ticket
    description: Add a mechanic to a service ticket. Mechanic must not already be assigned.
    security:
      - bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service ticket ID
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: Mechanic ID to assign
    responses:
      200:
        description: Mechanic assigned successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Mechanic already assigned to this ticket
      401:
        description: Missing or invalid token
      404:
        description: Service ticket or mechanic not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"error": "Mechanic already assigned to this ticket"}), 400

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
@mechanic_token_required
def remove_mechanic(current_mechanic_id, ticket_id, mechanic_id):
    """
    Remove a mechanic from a service ticket
    ---
    tags:
      - Service Tickets
    summary: Remove a mechanic from a ticket
    description: Unassign a mechanic from a service ticket.
    security:
      - bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service ticket ID
      - in: path
        name: mechanic_id
        type: integer
        required: true
        description: Mechanic ID to remove
    responses:
      200:
        description: Mechanic removed successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      400:
        description: Mechanic is not assigned to this ticket
      401:
        description: Missing or invalid token
      404:
        description: Service ticket or mechanic not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic is not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@mechanic_token_required
def edit_ticket_mechanics(current_mechanic_id, ticket_id):
    """
    Bulk edit mechanics on a service ticket
    ---
    tags:
      - Service Tickets
    summary: Bulk add/remove mechanics from a ticket
    description: Assign and unassign multiple mechanics in a single request using add_ids and remove_ids arrays.
    security:
      - bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service ticket ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/EditTicketPayload'
    responses:
      200:
        description: Mechanics updated successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      401:
        description: Missing or invalid token
      404:
        description: Service ticket not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.json or {}
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_ticket_bp.route("/<int:ticket_id>/add-part", methods=["POST"])
@mechanic_token_required
def add_part_to_ticket(current_mechanic_id, ticket_id):
    """
    Add a part/inventory item to a service ticket
    ---
    tags:
      - Service Tickets
    summary: Add a part to a service ticket
    description: Attach an inventory part to a ticket with a specified quantity. If the part is already on the ticket, quantity is incremented.
    security:
      - bearer: []
    parameters:
      - in: path
        name: ticket_id
        type: integer
        required: true
        description: Service ticket ID
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/AddPartPayload'
    responses:
      200:
        description: Part added successfully
        schema:
          $ref: '#/definitions/ServiceTicket'
      401:
        description: Missing or invalid token
      404:
        description: Service ticket or part not found
    """
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.json or {}
    inventory_id = data.get("inventory_id")
    quantity = data.get("quantity", 1)

    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    line_item = TicketInventory.query.filter_by(
        service_ticket_id=ticket_id, inventory_id=inventory_id
    ).first()

    if line_item:
        line_item.quantity += quantity
    else:
        line_item = TicketInventory(service_ticket_id=ticket_id, inventory_id=inventory_id, quantity=quantity)
        db.session.add(line_item)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200
