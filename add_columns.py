from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    try:
        db.engine.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20)")
        db.engine.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS cover_image VARCHAR(255)")
        db.engine.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS farm_size VARCHAR(50)")
        db.engine.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS crops VARCHAR(255)")
        db.engine.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT TRUE")
        print("Columns added successfully!")
    except Exception as e:
        print(f"Error: {e}")
