from app.extensions import ma
from app.models import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True

    password = ma.auto_field(load_only=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(only=("email", "password"))
