#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Recreate database schema from models
python << EOF
import os
from sqlalchemy import create_engine, text
from app import create_app, db

db_url = os.environ.get('DATABASE_URL')
if db_url:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    print("Schema reset")

app = create_app()
with app.app_context():
    db.create_all()
    print("Database recreated from models")
EOF
