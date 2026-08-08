from app import create_app
from app.database import db

app = create_app()

# Ensure tables are created
with app.app_context():
    db.create_all()
    print("✓ Database tables created")

# Run the app
app.run(host='0.0.0.0', port=5000, debug=False)