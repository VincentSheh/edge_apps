#!/bin/bash

# Start NGINX (RTMP-HLS)
/usr/local/nginx/sbin/nginx -g "daemon off;" &

# Start Flask
python3 /opt/app/app.py
