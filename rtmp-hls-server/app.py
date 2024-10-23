from flask import Flask, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

# Global variable to keep track of the FFmpeg process
ffmpeg_process = None

@app.route('/stream/initialize/<stream_key>', methods=['GET'])
def start_stream(stream_key):
    """Starts an FFmpeg process for streaming."""
    global ffmpeg_process

    # Define the FFmpeg command
    ffmpeg_command = [
        'ffmpeg', 
        '-re', 
        '-i', '/pv/video_files/Big Buck Bunny.mp4',
        '-c', 'copy', 
        '-f', 'flv', 
        'rtmp://localhost:1935/live/' + stream_key  # Using + for concatenation
    ]
    
    try:
        # Start the FFmpeg process and store its reference
        ffmpeg_process = subprocess.Popen(ffmpeg_command)
        return jsonify({"message": "Started stream for " + stream_key}), 200  # Using + for concatenation
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream/terminate/<stream_key>', methods=['GET'])
def stop_stream(stream_key):
    """Terminates the FFmpeg process associated with the given stream key."""
    global ffmpeg_process

    if ffmpeg_process is not None:
        try:
            # Terminate the FFmpeg process using its PID
            os.kill(ffmpeg_process.pid, signal.SIGTERM)  # Gracefully terminate
            ffmpeg_process.wait()  # Wait for the process to terminate
            print("Stopped streaming for " + stream_key + ".")  # Using + for concatenation
            ffmpeg_process = None  # Reset the process variable
            return jsonify({"message": "Stopped stream for " + stream_key}), 200  # Using + for concatenation
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No streaming process is currently running."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
