from flask import Flask, jsonify, request
import subprocess
import os
import signal

app = Flask(__name__)

# Global variable to hold the process
client_process = None

@app.route('/start-client', methods=['POST'])
def start_client():
    """Start the HLS client script with specified parameters."""
    
    global client_process

    # Extract parameters from the JSON request
    data = request.get_json()
    num_clients = data.get("n", 1)  # Default to 1 if not provided
    cpu = data.get("c", 1)          # Default to 1 if not provided
    file_to_write = data.get("f", "ingress__qoe_noatk_ingDeny.csv")  # Default file name
    duration = data.get("w", 90)    # Default to 90 seconds if not provided
    loop_flag = data.get("loop_flag", True)  # Default to True if not provided
    total_clients = data.get("tot_c", num_clients)
    id = data.get("u", 0)

    # Define the command to run, adding the loop flag
    command = [
        "python", "hls_client.py", 
        "-n", str(num_clients), 
        "-c", str(cpu), 
        "-f", file_to_write, 
        "-w", str(duration),
        "-l", str(loop_flag).lower(),  # Convert boolean to lowercase string for command line
        "-m", str(total_clients),
        "-u", str(id),
    ]
    
    try:
        # Run the command and store the process
        client_process = subprocess.Popen(command)
        return jsonify({"message": "HLS client started."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop-client', methods=['POST'])
def stop_client():
    """Stop the HLS client script if it's running."""
    
    global client_process
    
    if client_process is not None:
        try:
            # Terminate the process
            os.kill(client_process.pid, signal.SIGTERM)  # Gracefully terminate the process
            client_process = None  # Reset the process variable
            return jsonify({"message": "HLS client stopped."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No HLS client is currently running."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3050)
