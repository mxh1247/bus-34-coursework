from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models


def ensure_schema():
    with app.app_context():
        db.create_all()

        inspector = sa.inspect(db.engine)
        if "user_health_log" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("user_health_log")}

        def add_column_if_missing(column_name, ddl):
            if column_name in columns:
                return

            try:
                with db.engine.begin() as connection:
                    connection.execute(sa.text(ddl))
                columns.add(column_name)
            except sa.exc.OperationalError as exc:
                if "duplicate column name" not in str(exc).lower():
                    raise
                columns.add(column_name)

        add_column_if_missing(
            "admin_comment",
            "ALTER TABLE user_health_log ADD COLUMN admin_comment VARCHAR(256)",
        )
        add_column_if_missing(
            "water",
            "ALTER TABLE user_health_log ADD COLUMN water FLOAT",
        )


ensure_schema()
