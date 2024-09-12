
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import threading
import time
import numpy as np
import pandas as pd
import os
import math

url_list = ["http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Ftears-b%2Ftears-b.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",
            "http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Ftears-a%2Ftears-a.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",
            "http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Fnomor%2F1.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",
            "http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Fnomor%2F3.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",
            "http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Fnomor%2F3.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",
            "http://192.168.50.12:3000/samples/dash-if-reference-player/index_copy.html?mpd=http%3A%2F%2F192.168.50.12%3A8010%2Fnomor%2F5.mpd&autoLoad=true&muted=true+&debug.logLevel=5&streaming.capabilities.supportedEssentialProperties.0.schemeIdUri=urn%3Advb%3Adash%3Afontdownload%3A2014&streaming.capabilities.supportedEssentialProperties.1.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AColourPrimaries&streaming.capabilities.supportedEssentialProperties.2.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3AMatrixCoefficients&streaming.capabilities.supportedEssentialProperties.3.schemeIdUri=urn%3Ampeg%3AmpegB%3Acicp%3ATransferCharacteristics&streaming.capabilities.supportedEssentialProperties.4.schemeIdUri=http%3A%2F%2Fdashif.org%2Fthumbnail_tile&streaming.capabilities.supportedEssentialProperties.5.schemeIdUri=http%3A%2F%2Fdashif.org%2Fguidelines%2Fthumbnail_tile&streaming.delay.liveDelayFragmentCount=NaN&streaming.delay.liveDelay=NaN&streaming.buffer.initialBufferLevel=NaN&streaming.liveCatchup.maxDrift=NaN&streaming.liveCatchup.playbackRate.min=NaN&streaming.liveCatchup.playbackRate.max=NaN",]

def write_or_append_csv(file_path,df):
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', header=False, index=False)    
    return df  
def calculate_qoe(initial_startup_delay, bitrate, buffer_length, stall_count, stall_duration, client_id):
    
    if not (bitrate and buffer_length and stall_count and stall_duration):
        return None
    sampling_rate = 2.0
    # Calculate the Video Resolution 
    bitrate_arr = np.array(bitrate)[:,1]
    integrated_resolution = np.trapz(bitrate_arr, dx = sampling_rate)
    video_resolution = 1/(len(bitrate_arr)*sampling_rate)*integrated_resolution
    # Calculate Video Variation Rate
    bitrate_diff_arr = np.square(np.diff(bitrate_arr))
    integrated_variation_rate = np.trapz(bitrate_diff_arr, dx = sampling_rate)
    variation_rate = 1/(len(bitrate_diff_arr)*sampling_rate)*integrated_variation_rate
    # Get Initial Startup Delay
    initial_startup_delay = initial_startup_delay
    # Calculate Video Stalling
    stall_duration_arr = np.array(stall_duration)[:,1]
    stall_diff_arr = np.diff(stall_duration_arr) if len(stall_duration_arr) > 1 else stall_duration
    total_stall_duration = np.sum(stall_diff_arr) 
    
    # TODO: Normalize using Standard Normalization, when collecting data, record it in a csv and then get the mean and variance
    qoe = video_resolution - variation_rate - initial_startup_delay - total_stall_duration
    
    # TODO: Decide on the weight
    w_resolution = 0.2
    w_variation = 0.15
    w_startup_delay = 0.4
    w_stalling = 0.25    
    # Store the results in a DataFrame for easy output
    qoe_df = pd.DataFrame({
        'client_id': [client_id],
        'video_resolution': [video_resolution],
        'variation_rate': [variation_rate],
        'startup_delay': [initial_startup_delay],
        'total_stall_duration': [total_stall_duration],
        'time':[int(bitrate[-1][0])],
        f'qoe_{client_id}': [qoe]
    })    
    
    # ? Record QoE Data
    file_path = 'qoe_data.csv'
    write_or_append_csv(file_path, qoe_df)
    return qoe_df

  # TODO Create Convert to Pandas CSV
  
chrome_driver_path = '/opt/homebrew/Caskroom/chromedriver/127.0.6533.88/chromedriver-mac-arm64/chromedriver'
def emulate_client(client_id,results):
    # Specify the path to the ChromeDriver
    # initial_sleep_time = np.random.uniform(1,2)
    # watch_time = np.random.uniform(10,20)
    initial_sleep_time = np.random.uniform(5,20)
    watch_time = np.random.uniform(40,200)
    video_number = np.random.choice(5)
    print(video_number)
    # ? Random User Arrival
    time.sleep(initial_sleep_time)
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the ChromeDriver service
    service = Service(chrome_driver_path)
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Example: Open a URL
    # http://192.168.50.12:3000
    driver.get(url_list[video_number])
    

    # Initialize empty lists for metrics
    bitrate = []
    buffer = []
    stall_count = []
    stall_duration = []

    remaining_time = watch_time
    for i in range(math.ceil(remaining_time/60)):  # Assuming you want to loop half of the watch_time
        if remaining_time > 60:
          remaining_time -= 60
          sleep_time = 60 
        else:
          sleep_time = remaining_time
        time.sleep(sleep_time)  # Sleep for a smaller interval (2 seconds here)
        
        # Execute the custom function to get metrics
        driver.execute_script("angular.element(document.body).scope().getMetrics()")              
        # Retrieve the metrics from the global variable
        metrics = driver.execute_script("return window.metrics")
        
        # Append Metrics
        initial_startup_delay = metrics['initialStartupDelay']
        bitrate.extend(metrics['videoChartState']['bitrate']['data'])
        buffer.extend(metrics['videoChartState']['buffer']['data'])
        stall_count.extend(metrics['videoChartState']['stallCount']['data'])
        stall_duration.extend(metrics['videoChartState']['stallDuration']['data'])
        
    print("Finished Running, Aggregating QoE Scores...")

    query_metric_list = ['bitrate', 'buffer', 'index', 
                         'latency', 'stallCount', 'stallDuration']
    
    qoe_df = calculate_qoe(initial_startup_delay, bitrate, buffer, stall_count, stall_duration, client_id)
    
    driver.quit()
    results[client_id] = qoe_df[f"qoe_{client_id}"]

def main():
  while True:
    num_clients = 5
    threads = []
    results = {}
    
    for i in range(num_clients):
        thread = threading.Thread(target=emulate_client, args=(i,results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    # Combine all results into a single DataFrame
    combined_df = pd.DataFrame()
    for i in range(num_clients):
        client_df = results[i].copy()
        print(client_df)
        if combined_df.empty:
            combined_df = client_df
        else:
            # combined_df = pd.merge(combined_df, client_df, on="Time", how="outer")
            combined_df = pd.concat([combined_df, client_df], axis=1)
            print(combined_df)
    # Save the combined DataFrame to a CSV file
    write_or_append_csv("QoE_test.csv", combined_df)
    print("All QoE scores written to QoE_results.csv")

  # if os.path.exists(file_name):
  #       # Read the existing file
  #       existing_df = pd.read_csv(file_name, index_col=0)
  #       # Check if the 'Client ID' column matches
  #       if 'Client ID' in existing_df.columns and list(existing_df['Client ID']) == list(new_df['Client ID']):
  #           # Append new QoE Score as a new column
  #           column_name = f"QoE Score {len(existing_df.columns) - 1}"
  #           existing_df[column_name] = new_df['QoE Score']
  #       else:
  #           # If 'Client ID' doesn't match, raise an error or handle accordingly
  #           raise ValueError("Client ID columns do not match.")
  # else:
    
if __name__ == "__main__":
    main()
    
    
# def calculate_qoe(initial_startup_delay, bitrate, buffer_length, stall_count, stall_duration, client_id):
#     if not (bitrate and buffer_length and stall_count and stall_duration):
#         return None
    
#     qoe_scores = []
#     w_startup_delay = 0.2
#     w_bitrate = 0.3
#     w_buffer_length = 0.2
#     w_stall_count = 0.15
#     w_stall_duration = 0.15

#     max_startup_delay = 2.0
#     max_bitrate = 2000.0
#     max_buffer_length = 80.0
#     max_stall_count = 3
#     max_stall_duration = 10000.0

#     for i in range(len(bitrate)):
#         time, current_bitrate = bitrate[i]
#         _, current_buffer_length = buffer_length[i]
#         _, current_stall_count = stall_count[i]
#         _, current_stall_duration = stall_duration[i]

#         norm_startup_delay = 1 - (initial_startup_delay / max_startup_delay)
#         norm_bitrate = current_bitrate / max_bitrate
#         norm_buffer_length = current_buffer_length / max_buffer_length
#         norm_stall_count = 1 - (current_stall_count / max_stall_count)
#         norm_stall_duration = 1 - (current_stall_duration / max_stall_duration)

#         qoe_score = (w_startup_delay * norm_startup_delay +
#                      w_bitrate * norm_bitrate +
#                      w_buffer_length * norm_buffer_length +
#                      w_stall_count * norm_stall_count +
#                      w_stall_duration * norm_stall_duration)

#         qoe_scores.append((int(time), qoe_score))
    
#     print(f"Client ID: {client_id}")
#     for time, score in qoe_scores:
#         print(f"Time: {int(time)}, QoE Score: {score}")
        
#     qoe_df = pd.DataFrame(qoe_scores, columns=["Time", f"Client_{client_id}_QoE"])
#     return qoe_df    