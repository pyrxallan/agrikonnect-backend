#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Drop alembic version table to force fresh migration
python << EOF
import os
from sqlalchemy import create_engine, text

db_url = os.environ.get('DATABASE_URL')
if db_url:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.commit()
    print("Reset migration history")
EOF

# Run all migrations fresh
flask db upgrade
