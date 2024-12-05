FROM alqutami/rtmp-hls

# Modify the sources list to use the Debian archive for stretch and remove unavailable repositories
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    apt-get update

# Install Python, Flask, and FFmpeg
RUN apt-get install -y python3 python3-pip ffmpeg curl procps && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size
# Install Flask
RUN pip3 install flask

# Copy your Python Flask app and change a file to force cache busting
RUN echo "Force rebuild" > /tmp/force-rebuild  # This will change each build
COPY app.py /app.py
COPY Big_Buck_Bunny.mp4 /Big_Buck_Bunny.mp4


# Print Python version (optional for debugging)
RUN python3 --version

# Start the Flask app and Nginx
CMD ["sh", "-c", "python3 /app.py & nginx -g 'daemon off;'"]