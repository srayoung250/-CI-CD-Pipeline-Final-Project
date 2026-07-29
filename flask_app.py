import os
from app import create_app
from app.extensions import db
from config import ProductionConfig, DevelopmentConfig

flask_env = os.getenv("FLASK_ENV", "development")
config_class = ProductionConfig if flask_env == "production" else DevelopmentConfig

app = create_app(config_class)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=flask_env == "development")
