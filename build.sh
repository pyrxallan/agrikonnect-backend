#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Stamp database to current state and run migrations
flask db stamp head || true
flask db upgrade || flask db stamp head
