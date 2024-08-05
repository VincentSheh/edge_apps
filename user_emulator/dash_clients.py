
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import threading
import time
import numpy as np
import pandas as pd
import os
def calculate_qoe(initial_startup_delay, bitrate, buffer_length, stall_count, stall_duration, client_id):
  if not(bitrate):
    return None
  # Calculate average bitrate
  average_bitrate = np.mean([value for time, value in bitrate])

  # Calculate average buffer length
  average_buffer_length = np.mean([value for time, value in buffer_length])

  # Calculate total stall count
  total_stall_count = sum([value for time, value in stall_count])

  # Calculate total stall duration
  total_stall_duration = sum([value for time, value in stall_duration])

  # Define weights for each metric (example weights, can be adjusted)
  w_startup_delay = 0.2
  w_bitrate = 0.3
  w_buffer_length = 0.2
  w_stall_count = 0.15
  w_stall_duration = 0.15

  # Normalize metrics (example normalization, can be adjusted)
  max_startup_delay = 10.0  # Maximum acceptable startup delay
  max_bitrate = 10000.0  # Maximum bitrate
  max_buffer_length = 10.0  # Maximum buffer length
  max_stall_count = 10  # Maximum acceptable stall count
  max_stall_duration = 5000.0  # Maximum acceptable stall duration

  # Calculate normalized values
  norm_startup_delay = 1 - (initial_startup_delay / max_startup_delay)
  norm_bitrate = average_bitrate / max_bitrate
  norm_buffer_length = average_buffer_length / max_buffer_length
  norm_stall_count = 1 - (total_stall_count / max_stall_count)
  norm_stall_duration = 1 - (total_stall_duration / max_stall_duration)

  # Calculate QoE score
  qoe_score = (w_startup_delay * norm_startup_delay +
              w_bitrate * norm_bitrate +
              w_buffer_length * norm_buffer_length +
              w_stall_count * norm_stall_count +
              w_stall_duration * norm_stall_duration)
  print(client_id, qoe_score)
  return qoe_score
  # TODO Create Convert to Pandas CSV
  
chrome_driver_path = '/opt/homebrew/Caskroom/chromedriver/127.0.6533.88/chromedriver-mac-arm64/chromedriver'
def emulate_client(client_id,results):
    # Specify the path to the ChromeDriver
    
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the ChromeDriver service
    service = Service(chrome_driver_path)
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Example: Open a URL
    # http://192.168.50.12:3000
    driver.get("http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8001%2Ftears-a%2Ftears-a.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN")
    

    # Perform your automation tasks here
    time.sleep(30)
    # Execute the custom function to get metrics
    driver.execute_script("angular.element(document.body).scope().getMetrics()")
    
    # Retrieve the metrics from the global variable
    metrics = driver.execute_script("return window.metrics")
    
    # Print the retrieved metrics
    # print(json.dumps(metrics, indent=4))  
    # print(metrics['initialStartupDelay'])  
    query_metric_list = ['bitrate', 'buffer', 'index', 
                         'latency', 'stallCount', 'stallDuration']
    # for metric in query_metric_list:
    #     print(metric)
    #     print("Data:")
    #     for point in metrics['videoChartState'][metric]['data']:
    #         print(f"  Time: {point[0]}, Value: {point[1]}")    
    # Close the browser
    initial_startup_delay = metrics['initialStartupDelay']
    bitrate = metrics['videoChartState']['bitrate']['data']
    buffer = metrics['videoChartState']['buffer']['data']
    stall_count = metrics['videoChartState']['stallCount']['data']
    stall_duration = metrics['videoChartState']['stallDuration']['data']
    
    qoe_score = calculate_qoe(initial_startup_delay, bitrate, buffer, stall_count, stall_duration, client_id)
    driver.quit()
    results[client_id] = qoe_score

def main():
  num_clients = 3
  threads = []
  results = {client_id: 0 for client_id in range(num_clients)}
  for i in range(num_clients):
    thread = threading.Thread(target=emulate_client, args=(i,results))
    threads.append(thread)
    thread.start()
  for thread in threads:
    thread.join()
  file_name = f"QoE_{num_clients}_values.csv"
  new_df = pd.DataFrame(list(results.items()), columns=['Client ID', 'QoE Score'])

  if os.path.exists(file_name):
        # Read the existing file
        existing_df = pd.read_csv(file_name, index_col=0)
        # Check if the 'Client ID' column matches
        if 'Client ID' in existing_df.columns and list(existing_df['Client ID']) == list(new_df['Client ID']):
            # Append new QoE Score as a new column
            column_name = f"QoE Score {len(existing_df.columns) - 1}"
            existing_df[column_name] = new_df['QoE Score']
        else:
            # If 'Client ID' doesn't match, raise an error or handle accordingly
            raise ValueError("Client ID columns do not match.")
  else:
        existing_df = new_df

    # Save the DataFrame to CSV
  existing_df.to_csv(file_name)
    
if __name__ == "__main__":
    main()