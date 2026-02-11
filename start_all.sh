#!/bin/bash

# Start notification service in background
cd microservices/notifications/app
python app.py &
NOTIF_PID=$!

# Start main Flask app
cd ../../..
python run.py &
MAIN_PID=$!

# Wait for both processes
wait $NOTIF_PID $MAIN_PID
