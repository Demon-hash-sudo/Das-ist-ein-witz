#!/bin/bash

# Start the simple-media-server.py script
python simple-media-server.py &

# Wait for 20 seconds
sleep 20

# Activate the virtual environment
source venv/bin/activate

# Start the send_url_to_tv.py script
python send_url_to_tv.py