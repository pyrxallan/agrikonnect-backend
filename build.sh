#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Recreate database schema from models
python << EOF
import os
from app import create_app, db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database recreated from models")
EOF
