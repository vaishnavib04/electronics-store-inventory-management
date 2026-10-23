from app import create_app
from app.extensions import db
import app.models

app = create_app()

with app.app_context():
    db.create_all()
    print("ESIMS database tables created successfully!")
    print("Tables:", sorted(db.metadata.tables.keys()))