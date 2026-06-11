from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from typing import Any

db = SQLAlchemy()
migrate = Migrate()


def init_db(app) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def create_tables(app) -> None:
    with app.app_context():
        db.create_all()


def drop_tables(app) -> None:
    with app.app_context():
        db.drop_all()


def reset_database(app) -> None:
    with app.app_context():
        db.drop_all()
        db.create_all()
