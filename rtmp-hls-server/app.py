from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/stream/<stream_key>', methods=['GET'])
def start_stream(stream_key):
    # Correctly concatenate the stream URL
    ffmpeg_command = [
        'ffmpeg', '-re', '-i', '/home/wmnlab/edge_apps/video_files/Big Buck Bunny.mp4',
        '-c', 'copy', '-f', 'flv', 'rtmp://localhost:1935/live/' + stream_key
    ]
    try:
        subprocess.Popen(ffmpeg_command)  # Start the FFmpeg process
        return jsonify({"message": "Started stream for " + stream_key}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_stream/<stream_key>', methods=['GET'])
def stop_stream(stream_key):
    try:
        subprocess.run(['pkill', '-f', stream_key])  # Kill the process associated with the stream_key
        return jsonify({"message": "Stopped stream for " + stream_key}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
