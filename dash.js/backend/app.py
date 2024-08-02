from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
def calculate_qoe(initial_delay, total_stall_duration, stall_count, bitrate_switch_count, average_bitrate):
    """
    Calculate the QoE (Quality of Experience) for video streaming.

    Parameters:
    - initial_delay (float): Initial buffering delay in seconds.
    - total_stall_duration (float): Total duration of all stalling events in seconds.
    - stall_count (int): Number of stalling events.
    - bitrate_switch_count (int): Number of bitrate switches.
    - average_bitrate (float): Average bitrate of the video in kbps.

    Returns:
    - qoe (float): Calculated QoE score.
    """
    # Weights for each factor (example weights based on research insights)
    w_initial_delay = 0.15
    w_total_stall_duration = 0.4
    w_stall_count = 0.25
    w_bitrate_switch = 0.1
    w_average_bitrate = 0.1

    # Normalize values to a standard scale (0-100)
    norm_initial_delay = min(100, initial_delay * 10)
    norm_total_stall_duration = min(100, total_stall_duration * 10)
    norm_stall_count = min(100, stall_count * 10)
    norm_bitrate_switch_count = min(100, bitrate_switch_count * 10)
    norm_average_bitrate = min(100, average_bitrate / 10)

    # Calculate QoE using weighted sum
    qoe = 100 - (
        w_initial_delay * norm_initial_delay +
        w_total_stall_duration * norm_total_stall_duration +
        w_stall_count * norm_stall_count +
        w_bitrate_switch * norm_bitrate_switch_count +
        w_average_bitrate * norm_average_bitrate
    )

    # Ensure QoE is within the valid range (0-100)
    return max(0, min(100, qoe))
  
@app.route("/")
def check_availability():
  print("Hello, Server is running")
  return "Server is Running"

@app.route('/calculate_qoe', methods=['POST'])
def calculate_qoe_endpoint():
    print("I RUN")
    data = request.json
    initial_delay = data.get('initial_delay', 0.0)
    total_stall_duration = data.get('total_stall_duration', [])
    stall_count = data.get('stall_count', [])
    bitrate_switch_count = data.get('bitrate_switch_count', [])
    average_bitrate = data.get('average_bitrate', [])

    # qoe_score = calculate_qoe(initial_delay, total_stall_duration, stall_count, bitrate_switch_count, average_bitrate)
    print(data)
    return jsonify({"qoe_score": "TEST"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)