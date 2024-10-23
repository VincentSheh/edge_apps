import time
import subprocess
import requests
# TODO:
atk_detection_config_dict = {}
# Define the list of resource configurations for each iteration
resource_configurations = [
    {"cpu": "0.5", "memory": "1000m"}, # Memory is currently unfixed
    {"cpu": "1", "memory": "1000m"},
    {"cpu": "1.5", "memory": "1000m"},
    {"cpu": "2", "memory": "1000m"},
    {"cpu": "2.5", "memory": "1000m"},
    {"cpu": "3", "memory": "1000m"},
    # Add more configurations as needed
]

# Define the base URLs for the APIs
modify_deployment_url = "http://192.168.50.157:5000/modify-deployment"
start_capture_url = "http://192.168.50.181:3050/start-capture"
stop_capture_url = "http://192.168.50.181:3050/terminate-capture"
start_client_url = "http://192.168.50.12:3050/start-client"
start_attacker_url = "http://192.168.50.130:3050/start-bonesi"
stop_attacker_url = "http://192.168.50.130:3050/stop-bonesi"
stop_client_url = "http://192.168.50.12:3050/stop-client"

def modify_deployment(cpu, memory):
    """Modify the deployment with the given CPU and memory."""
    payload = {
        "deployment_name": "hls-ls-deployment",
        "cpu": cpu,
        "memory": memory
    }
    response = requests.patch(modify_deployment_url, json=payload)
    payload = {
        "deployment_name": "deepod-detector-deployment",
        "cpu": 4-cpu,
        "memory": memory
    }
    response = requests.patch(modify_deployment_url, json=payload)    
    return response.status_code == 200

def start_capture():
    """Start the packet capture."""
    response = requests.post(start_capture_url)
    return response.status_code == 200

def stop_capture():
    """Stop the packet capture."""
    response = requests.post(stop_capture_url)
    return response.status_code == 200

def start_client(n_clients, cpu, duration):
    """Start the HLS client."""
    payload = {
        "n": n_clients,
        "c": cpu,
        "f": "ingress_qoe_noatk_noids.csv",
        "w": duration,
        "loop_flag": False
    }
    response = requests.post(start_client_url, json=payload)
    return response.status_code == 200

def start_attacker():
    """Start the Bonesi attack."""
    payload = {
        "protocol": "tcp",
        "url": "http://hlslivestream.com",
        "send_rate": 5000,
        "device": "enp0s3",
        "dst_ip_port": "192.168.50.30:80"
    }
    response = requests.post(start_attacker_url, json=payload)
    return response.status_code == 200

def stop_attacker():
    """Stop the Bonesi attack."""
    response = requests.post(stop_attacker_url)
    return response.status_code == 200

def stop_client():
    """Stop the HLS client."""
    response = requests.post(stop_client_url)
    return response.status_code == 200

def main():
        for config in resource_configurations:
          cpu = config["cpu"]
          memory = config["memory"]
          for n_clients in range(3): 
            for i in range(5): # Repeat 5 Times
              # Modify the deployment
              if modify_deployment(cpu, memory):
                  print(f"Modified deployment: CPU={cpu}, Memory={memory}")
                  time.sleep(10)  # Wait for pods to start

                  # Start packet capture
                  if start_capture():
                      print("Packet capture started.")

                      # Start HLS client
                      if start_client(n_clients, cpu, duration=90):
                          print("HLS client started.")

                          # Start Bonesi attack
                          if start_attacker():
                              print("Bonesi attack started.")

                              # Wait for 120 seconds
                              time.sleep(120)

                              # Stop Bonesi attack
                              if stop_attacker():
                                  print("Bonesi attack stopped.")

                              # Stop HLS client
                              if stop_client():
                                  print("HLS client stopped.")

                              # Stop packet capture
                              if stop_capture():
                                  print("Packet capture stopped.")
                          else:
                              print("Failed to start Bonesi attack.")
                      else:
                          print("Failed to start HLS client.")
                  else:
                      print("Failed to start packet capture.")
              else:
                  print("Failed to modify deployment.")
              time.sleep(10)

if __name__ == '__main__':
    main()
