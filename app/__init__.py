import os
from flask import Flask

from app.extensions import db, ma, limiter, cache, swagger
from app.swagger_definitions import swagger_template
from config import DevelopmentConfig, ProductionConfig


def create_app(config_class=None):
    if config_class is None:
        flask_env = os.getenv("FLASK_ENV", "development")
        config_class = ProductionConfig if flask_env == "production" else DevelopmentConfig
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    swagger.init_app(app)
    app.config["SWAGGER"] = swagger_template

    from app.blueprints.customer import customer_bp
    from app.blueprints.mechanic import mechanic_bp
    from app.blueprints.service_ticket import service_ticket_bp
    from app.blueprints.inventory import inventory_bp

    app.register_blueprint(customer_bp, url_prefix="/customers")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanics")
    app.register_blueprint(service_ticket_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    return app
