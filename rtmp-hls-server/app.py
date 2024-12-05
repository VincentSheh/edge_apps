from flask import Flask, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

# Dictionary to keep track of multiple FFmpeg processes
ffmpeg_processes = {}

@app.route('/stream/initialize/<stream_key>', methods=['GET'])
def start_stream(stream_key):
    """Starts an FFmpeg process for streaming."""
    # Define the FFmpeg command
    ffmpeg_command = [
        "ffmpeg", 
        "-re", 
        "-i", "./Big_Buck_Bunny.mp4",  # Input file, be sure to handle spaces correctly
        "-c:v", "libx264", "-b:v", "2000k", "-maxrate", "2000k", "-bufsize", "4000k", 
        "-c:a", "aac", "-b:a", "128k", 
        "-g", "60", "-bf", "2", 
        "-f", "flv", 
        'rtmp://localhost:1935/live/' + stream_key  # RTMP output URL
    ]
    
    try:
        # Start the FFmpeg process and store it in the dictionary with stream_key as the key
        ffmpeg_process = subprocess.Popen(ffmpeg_command)
        ffmpeg_processes[stream_key] = ffmpeg_process
        return jsonify({"message": "Started stream for " + stream_key}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream/terminate/<stream_key>', methods=['GET'])
def stop_stream(stream_key):
    """Terminates the FFmpeg process associated with the given stream key."""
    if stream_key in ffmpeg_processes:
        ffmpeg_process = ffmpeg_processes[stream_key]
        try:
            # Terminate the FFmpeg process using its PID
            os.kill(ffmpeg_process.pid, signal.SIGTERM)  # Gracefully terminate
            ffmpeg_process.wait()  # Wait for the process to terminate
            print("Stopped streaming for " + stream_key + ".")
            del ffmpeg_processes[stream_key]  # Remove the process from the dictionary
            return jsonify({"message": "Stopped stream for " + stream_key}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No streaming process is currently running for " + stream_key}), 400

@app.route('/stream/status', methods=['GET'])
def stream_status():
    """Returns a dictionary of currently running FFmpeg processes."""
    running_streams = {key: value.pid for key,value in ffmpeg_processes.items()}
    return jsonify({"running_streams": running_streams}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
