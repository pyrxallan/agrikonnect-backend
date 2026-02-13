#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Clear alembic version table and stamp to head
python << EOF
import os
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
if db_url:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM alembic_version"))
        conn.commit()
    print("Cleared migration history")
EOF

# Stamp to head (mark all migrations as applied) then upgrade
flask db stamp head
flask db upgrade
