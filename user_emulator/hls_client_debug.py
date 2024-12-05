import argparse
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
# from webdriver_manager.chrome import ChromeDriverManager

import threading
import time
import numpy as np
import pandas as pd
import os
import math
import requests
GREEN = "\033[92m"  # Bright green
RESET = "\033[0m"   # Reset to default color
RED = "\033[91m"  # Bright red


num_clients = 3
n_cpu_cores = 3000
file_path = 'k8s_qoe_atk_ids.csv'
# initial_sleep_time = np.random.uniform(1,2)
# watch_time = np.random.uniform(20,25)
# initial_sleep_time = np.random.uniform(5,20)
# watch_time = np.random.uniform(40,200)
initial_sleep_time = 0
watch_time = 90

url_list = [
    "http://192.168.50.12:8080/demo/index.html?src=http%3A%2F%2Fhlslivestream.com%2Fhls%2Ftest0.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://192.168.50.12:8080/demo/index.html?src=http%3A%2F%2Fhlslivestream.com%2Fhls%2Ftest1.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://192.168.50.12:8080/demo/index.html?src=http%3A%2F%2Fhlslivestream.com%2Fhls%2Ftest2.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://192.168.50.12:8080/demo/index.html?src=http%3A%2F%2Fhlslivestream.com%2Fhls%2Ftest3.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
            ]
def control_ffmpeg(control, key):
    url = f'http://hlslivestream.com/stream/{control}/{key}'
    try:
        # Send GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            print("Success:", response.json())  # Assuming the response is JSON
        else:
            print(f"Failed with status code: {response.status_code}")
            print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        
def write_or_append_csv(path, df):
    if not os.path.isfile(path):
        df.to_csv(path, index=False)
    else:
        df.to_csv(path, mode='a', header=False, index=False)    
    return df  
def calculate_qoe(metrics, client_id, tend, media_loading_time):
    # Get Metrics Dataframe
    tend = tend
    buffer_df = pd.DataFrame(metrics['buffer'])
    if buffer_df.shape[0] <= 1:
        qoe_df = pd.DataFrame({
            'client_id': [client_id],
            'video_resolution': [None],
            'variation_rate': [None],
            'startup_delay': [None],
            'avg_stall_duration': [None],
            f'qoe_{client_id}': [0]
        })            
        qoe_df['cpu'] = n_cpu_cores
        qoe_df['user'] = num_clients
        qoe_df['watch_time'] = watch_time
        print(RED + "Streaming Failed" + RESET)
        write_or_append_csv(file_path,qoe_df)
        return qoe_df
        
    level_df = pd.DataFrame(metrics['level'])
    level_to_bitrate_map = {2: 1125, 1: 438, 0: 281}
    level_df.loc[:,'levelBR'] = level_df['id'].map(lambda x : level_to_bitrate_map[x])    
   
    # Update Buffer and Level to Include the termination time
    last_row_buffer_df = buffer_df.iloc[-1].copy()
    last_row_buffer_df['time'] = tend
    buffer_df = pd.concat([buffer_df, pd.DataFrame([last_row_buffer_df])], ignore_index=True)    
    last_row_level_df = level_df.iloc[-1].copy()
    last_row_level_df['time'] = tend
    level_df = pd.concat([level_df, pd.DataFrame([last_row_level_df])], ignore_index=True)    
    #? Get Initial Startup Delay
    startup_delay = np.diff(buffer_df['time'].values[:2])[0]    
    #? Get Video Resolution
    prod_arr = level_df['levelBR'].values * level_df['time'].values
    video_resolution = np.sum(prod_arr)/np.sum(level_df['time'].values)
    
    #? Get Variation Ratio
    if level_df.shape[1] == 1:
        video_variation_rate = level_df['bitrate'].values[0] * level_df['time'].values[0]
    else:
        bitrate_diff_arr = np.square(np.diff(level_df['levelBR'].values))
        time_diff_arr = np.diff(level_df['time'].values)
        video_variation_rate = np.sum(bitrate_diff_arr*time_diff_arr)/level_df['time'].values[-1]
        
    #? Get Stalling Ratio
    buffer_df['stall'] = (buffer_df['buffer'] == 0).astype(int)
    buffer_df['time_diff'] = buffer_df['time'].diff()
    buffer_df.loc[0,'time_diff'] = 0
    stall_duration = buffer_df.loc[buffer_df['stall']==1, 'time_diff'].sum()
    average_stall_duration = stall_duration/tend
    
    
    # TODO: Normalize using Standard Normalization, when collecting data, record it in a csv and then get the mean and variance
    qoe = video_resolution - video_variation_rate - startup_delay - stall_duration
    
    # TODO: Decide on the weight
    w_resolution = 0.2
    w_variation = 0.15
    w_startup_delay = 0.4
    w_stalling = 0.25    
    # Store the results in a DataFrame for easy output
    qoe_df = pd.DataFrame({
        'client_id': [client_id],
        'video_resolution': [video_resolution],
        'variation_rate': [video_variation_rate],
        'startup_delay': [startup_delay],
        'avg_stall_duration': [average_stall_duration],
        'media_loading_duration': [media_loading_time * 1000],
        f'qoe': [qoe]
    })    
    
    # ? Record QoE Data
    qoe_df['cpu'] = n_cpu_cores
    qoe_df['user'] = num_clients
    qoe_df['watch_time'] = watch_time
    print(GREEN + file_path + RESET)
    write_or_append_csv(file_path,qoe_df)
    return qoe_df

#   # TODO Create Convert to Pandas CSV
def emulate_client(client_id, results):
    """Simulate a client watching a stream and collecting metrics."""    
    time.sleep(initial_sleep_time)  # Simulate random user arrival
    # ? Initialize the ffmpeg    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--remote-debugging-port={9222 + client_id}")  # Enable remote debugging
    # Initialize the Chrome WebDriver
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Open the streaming URL
    driver.get(f"http://192.168.50.12:8080/demo/index.html?src=http%3A%2F%2Fhlslivestream.com%2Fhls%2Ftest{client_id}.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==")
    button = driver.find_element("name", "config-apply")
    remaining_time = watch_time
    start_time = time.time()
    # Start the timer to measure media loading time
    start_time = time.time()

    # Loop to check if the stream has started (based on buffer availability)
    while True:
        # Retrieve metrics from the JavaScript function
        tempMetrics = driver.execute_script("return getMetrics();")
        # Wait a little before the next check
        time.sleep(0.5)
        
        # Check if the buffer has loaded (indicating the stream has started)
        if len(tempMetrics["video"]) > 2:
            media_loading_time = time.time() - start_time
            remaining_time -= media_loading_time
            
            print(GREEN + f"Buffer is not empty, Media Load Time {media_loading_time} seconds." + RESET)
            break
        print(RED + "Streaming Not Initialized, Refreshing..." + RESET)
        
        # Click the button to reapply configuration or refresh the player
        button.click()
        
        # Sleep a little before checking again
        time.sleep(1)
        
        # If the total remaining time exceeds the timeout, stop the process
        if time.time() - start_time > remaining_time:
            print("Timeout reached, stopping checks.")
            remaining_time = 0
            media_loading_time = time.time() - start_time
            break

    # Proceed with streaming for the remaining time
    time.sleep(remaining_time)


        
    # Retrieve metrics from the browser
    jsonMetrics = driver.execute_script("return getMetrics();")  # Get metrics from JavaScript
    tend = driver.execute_script("return performance.now() - events.t0")  # Get elapsed time

    # Calculate QoE
    metrics = jsonMetrics
    _ = calculate_qoe(metrics, client_id, tend, media_loading_time)
    
    # Terminate the Stream
    driver.quit()
            
def main():
    """Main function to parse arguments and start client simulations."""
    global num_clients, n_cpu_cores, file_path, watch_time
    
    parser = argparse.ArgumentParser(description='Set the configurations')
    parser.add_argument('-n', '--num_clients', type=int, help="Number of clients to stream")
    parser.add_argument('-c', '--cpu', type=float, help="Number of CPU allocated for the container")
    parser.add_argument('-f', '--file_path', type=str, help="Save the QoE data to a selected file")
    parser.add_argument('-w', '--watch_time', type=int, help="Watch Duration", default=60)
    parser.add_argument('-l', '--loop_flag', type=bool, help="Whether to Loop", default=True)
    
    args = parser.parse_args()

    # Update global variables if arguments are provided
    if args.num_clients is not None:
        num_clients = args.num_clients
    if args.cpu is not None:
        n_cpu_cores = args.cpu
    if args.file_path is not None:
        file_path = args.file_path
    if args.watch_time is not None:
        watch_time = args.watch_time  
    if args.loop_flag is not None:
        loop_flag = args.loop_flag  

    threads = []
    
    try:
        # while loop_flag:
            client_ids = [0]
            for i in client_ids:
                thread = threading.Thread(target=emulate_client, args=(i, {}))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()  # Wait for all threads to finish

    except KeyboardInterrupt:
        print("Interrupted! Stopping all clients...")
        stop_flag = True  # Set the stop flag to signal threads to stop
        for i in client_ids:
            print(f"Terminating Stream for client {i}")
        
        for thread in threads:
            thread.join()  # Ensure all threads have finished

if __name__ == "__main__":
    main()
    
    
    
    
  
# # chrome_driver_path = '/opt/homebrew/bin/chromedriver'
# chrome_driver_path = '/usr/local/bin/chromedriver'
# chromium_path = '/usr/bin/chromium-browser'
# def emulate_client(client_id,results):
#     # Specify the path to the ChromeDriver


#     # ? Random User Arrival
#     time.sleep(initial_sleep_time)
#     # Set up Chrome options
#     chrome_options = Options()
#     chrome_options.binary_location = chromium_path
#     chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
#     chrome_options.add_argument(f"--remote-debugging-port={9222+client_id}")  # Enable remote debugging
#     chrome_options.add_argument("--disable-software-rasterizer")    
#     # Set up the ChromeDriver service
#     service = Service(chrome_driver_path)
#     # Initialize the Chrome WebDriver
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     # driver = webdriver.Chrome(ChromeDriverManager().install()) #Use WebDriverManager Instead

#     driver.get(url_list[client_id])
#     # driver.get(url_list[0])
#     # driver.get("http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.54%3A30002%2Fhls%2Ftest.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==")
    

#     # Initialize empty lists for metrics
#     bitrate = []
#     buffer = []
#     stall_count = []
#     stall_duration = []

#     remaining_time = watch_time
#     for i in range(math.ceil(remaining_time/60)):  # Assuming you want to loop half of the watch_time
#         if remaining_time > 60:
#           remaining_time -= 60
#           sleep_time = 60 
#         else:
#           sleep_time = remaining_time
#         time.sleep(sleep_time)  # Sleep for a smaller interval (2 seconds here)
        
#         # button = driver.find_element_by_name('config-apply')
#         # button.click()        
#         # Retrieve the metrics from the global variable
#     jsonMetrics = driver.execute_script("""
#         console.log(getMetrics());  // This will print the result to the browser's console
#         return getMetrics();        // This returns the result to Python
#     """)
#     tend = driver.execute_script("return performance.now()-events.t0")
    
#     # with open("sample.json", "w") as outfile:
#     #     json.dump(jsonMetrics, outfile)
#     print("Finished Running, Aggregating QoE Scores...")
#     metrics = jsonMetrics
#     _ = calculate_qoe(metrics, client_id, tend)
#     driver.quit()

# def main():
# #   n_client_config = [3,3,3,2,2,2,1,1,1]
# #   for num_clients in n_client_config:
#     parser = argparse.ArgumentParser(description='Set the configurations')
#     parser.add_argument('-n', '--num_clients', type=int, help="Number of clients to stream")
#     parser.add_argument('-c', '--cpu', type=float, help="Numer of Cpu allocated for the container")
#     parser.add_argument('-f', '--file_path', type=str, help="Save the QoE Data selected file")
#     parser.add_argument('-w', '--watch_duration', type=int, help="Watch Duration", default=60)
#     args = parser.parse_args()

#     # Update global variables if arguments are provided
#     if args.num_clients is not None:
#         num_clients = args.num_clients
#     if args.cpu is not None:
#         n_cpu_cores = args.cpu
#     if args.file_path is not None:
#         file_path = args.file_path
#     if args.watch_duration is not None:
#         watch_duration = args.watch_duration  
#     #python hls_client.py -n 1 -c 2.5 -f 'k8s_qoe_noatk_no_ids.csv' -w 60
#     while (True):
#         threads = []
#         results = {}
#         # emulate_client(0,results)
#         for i in range(num_clients):
#             thread = threading.Thread(target=emulate_client, args=(i,results))
#             threads.append(thread)
#             thread.start()
        
#         for thread in threads:
#             thread.join()



# if __name__ == "__main__":
#     main()
 
 
 
    #  # Loop to check if the stream has started (based on buffer availability)
    # while True:
    #     # Retrieve metrics from the JavaScript function
    #     tempMetrics = driver.execute_script("return getMetrics();")
    #     print(tempMetrics)
    #     # Wait a little before the next check
    #     time.sleep(0.5)
        
    #     # Check if the buffer has loaded (indicating the stream has started)
    #     if len(tempMetrics["buffer"]) != 0:
    #         media_loading_time = time.time() - start_time
    #         remaining_time -= media_loading_time
            
    #         print(f"Buffer is not empty, Media Load Time {media_loading_time} seconds.")
    #         break
    #     # If the time exceeds the allowed threshold, refresh the stream
    #     elif (time.time() - start_time > 10):  # 5 seconds for refresh attempts
    #         print(RED + "Streaming Not Initialized, Refreshing..." + RESET)
            
    #         # Click the button to reapply configuration or refresh the player
    #         button.click()
            
    #         # Sleep a little before checking again
    #         time.sleep(5)
            
    #         # If the total remaining time exceeds the timeout, stop the process
    #         if time.time() - start_time > remaining_time:
    #             print("Timeout reached, stopping checks.")
    #             remaining_time = 0
    #             media_loading_time = time.time() - start_time
    #             break

    # # Proceed with streaming for the remaining time
    # time.sleep(remaining_time)