#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Run database migrations
flask db upgrade
