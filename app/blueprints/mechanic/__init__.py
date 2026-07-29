from flask import Blueprint

mechanic_bp = Blueprint("mechanic_bp", __name__)

from app.blueprints.mechanic import routes
