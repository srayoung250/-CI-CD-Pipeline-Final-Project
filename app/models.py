from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

service_mechanics = db.Table(
    "service_mechanics",
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_ticket.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanic.id"), primary_key=True),
)


class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship("ServiceTicket", back_populates="customer", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class Mechanic(db.Model):
    __tablename__ = "mechanic"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    service_tickets = db.relationship(
        "ServiceTicket", secondary=service_mechanics, back_populates="mechanics"
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class ServiceTicket(db.Model):
    __tablename__ = "service_ticket"

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(50), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_desc = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)

    customer = db.relationship("Customer", back_populates="service_tickets")
    mechanics = db.relationship(
        "Mechanic", secondary=service_mechanics, back_populates="service_tickets"
    )
    ticket_inventories = db.relationship(
        "TicketInventory", back_populates="service_ticket", cascade="all, delete-orphan"
    )
    parts = db.relationship("Inventory", secondary="ticket_inventory", viewonly=True)


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

    ticket_inventories = db.relationship(
        "TicketInventory", back_populates="inventory", cascade="all, delete-orphan"
    )


class TicketInventory(db.Model):
    """Junction model linking ServiceTicket <-> Inventory, with a quantity of parts used."""

    __tablename__ = "ticket_inventory"

    id = db.Column(db.Integer, primary_key=True)
    service_ticket_id = db.Column(db.Integer, db.ForeignKey("service_ticket.id"), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    service_ticket = db.relationship("ServiceTicket", back_populates="ticket_inventories")
    inventory = db.relationship("Inventory", back_populates="ticket_inventories")
