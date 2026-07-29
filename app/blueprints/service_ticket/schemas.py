from app.extensions import ma
from app.models import ServiceTicket


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = ma.Nested("MechanicSchema", many=True, only=("id", "name", "email"), dump_only=True)
    parts = ma.Nested("InventorySchema", many=True, only=("id", "name", "price"), dump_only=True)

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
