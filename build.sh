#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Clear migration history and apply fresh migrations
flask db stamp --purge 2>/dev/null || true
flask db upgrade
