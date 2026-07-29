from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True

    password = ma.auto_field(load_only=True)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicSchema(only=("email", "password"))
