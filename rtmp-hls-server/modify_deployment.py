from flask import Flask, request, jsonify
from kubernetes import client, config

app = Flask(__name__)

# Load Kubernetes configuration
# config.load_incluster_config()  # Use this if running in a pod
config.load_kube_config()  # Uncomment this if running locally with kubeconfig

@app.route('/modify-deployment', methods=['PATCH'])
def modify_deployment():
    """Modify the CPU and Memory requests of a Kubernetes deployment."""
    data = request.get_json()
    deployment_name = data.get("deployment_name")
    new_cpu = data.get("cpu")  # Expected format: "2000m" or "1"
    new_memory = data.get("memory")  # Expected format: "512Mi" or "1Gi"

    if not deployment_name or not new_cpu or not new_memory:
        return jsonify({"error": "Please provide 'deployment_name', 'cpu', and 'memory'."}), 400

    # Define the patch
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "hls-ls-app",  # Replace with your actual container name
                            "resources": {
                                "requests": {
                                    "cpu": new_cpu,
                                    # "memory": new_memory
                                },
                            "limits": {
                                "cpu": new_cpu,  # Set limits to match the requests or higher
                                # "memory": new_memory
                            }
                            }
                        }
                    ]
                }
            }
        }
    }

    # Create a Kubernetes API client
    k8s_client = client.AppsV1Api()

    # Patch the deployment
    try:
        response = k8s_client.patch_namespaced_deployment(
            name=deployment_name,
            namespace='default',  # Change this if your deployment is in a different namespace
            body=patch
        )
        return jsonify({"message": f"Updated deployment '{deployment_name}' with CPU: {new_cpu} and Memory: {new_memory}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3050)
