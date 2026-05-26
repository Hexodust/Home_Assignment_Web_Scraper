__version__ = "0.1"

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from project.config import config

toolbar = DebugToolbarExtension()
db = SQLAlchemy()

def create_app(config_name=None):
    import os

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask("project")
    app.config.from_object(config[config_name])

    app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://flask:flask@postgres:5432/flask_dev'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    toolbar.init_app(app)
    db.init_app(app)

    from project.controllers.printer import printer_bp
    from project.controllers.products import products_blueprint

    app.register_blueprint(printer_bp)
    app.register_blueprint(products_blueprint)

    return app
