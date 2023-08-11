#!/bin/bash

# Start your Django web app
echo "Starting Django web app..."
python manage.py runserver &

# Wait for the web app to start
sleep 5

# Start OWASP ZAP
echo "Starting OWASP ZAP..."
zap.sh -daemon -config api.disablekey=true &

# Wait for ZAP to start
sleep 5

# Configure ZAP to use the web app as a target
echo "Configuring ZAP..."
zap-cli --zap-url http://localhost:8090/ context new
zap-cli --zap-url http://localhost:8090/ context include '.*'
zap-cli --zap-url http://localhost:8090/ context exclude '.*(\\.css|\\.js|\\.png|\\.jpeg|\\.jpg|\\.gif)$'
zap-cli --zap-url http://localhost:8090/ target set "http://localhost:8000"

# Spider the web app
echo "Spidering the web app..."
zap-cli --zap-url http://localhost:8090/ spider scan --context 1

# Wait for the spider to complete
sleep 5

# Perform an active scan
echo "Performing an active scan..."
zap-cli --zap-url http://localhost:8090/ active-scan --context 1

# Wait for the active scan to complete
sleep 5

# Generate a report
echo "Generating ZAP report..."
zap-cli --zap-url http://localhost:8090/ report -o zap_report.html -f html

# Stop OWASP ZAP
echo "Stopping OWASP ZAP..."
zap-cli --zap-url http://localhost:8090/ core shutdown

# Stop your Django web app
echo "Stopping Django web app..."
kill $(lsof -t -i :8000)
