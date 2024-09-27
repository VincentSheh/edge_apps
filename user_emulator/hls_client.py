import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

import threading
import time
import numpy as np
import pandas as pd
import os
import math
num_clients = 3
n_cpu_cores = 1000
file_path = 'qoe_data_hls.csv'
# initial_sleep_time = np.random.uniform(1,2)
# watch_time = np.random.uniform(20,25)
# initial_sleep_time = np.random.uniform(5,20)
# watch_time = np.random.uniform(40,200)
initial_sleep_time = 0
watch_time = 200

url_list = [
    "http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.54%3A30002%2Fhls%2Ftest.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.54%3A30002%2Fhls%2Ftest2.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.54%3A30002%2Fhls%2Ftest3.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
    "http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.12%3A8080%2Fhls%2Ftest.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==",
            ]
def write_or_append_csv(path, df):
    if not os.path.isfile(path):
        df.to_csv(path, index=False)
    else:
        df.to_csv(path, mode='a', header=False, index=False)    
    return df  
def calculate_qoe(metrics, client_id, tend):
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
        write_or_append_csv(file_path,qoe_df)
        qoe_df['cpu'] = n_cpu_cores
        qoe_df['user'] = num_clients
        qoe_df['watch_time'] = watch_time
        write_or_append_csv("qoe_data_hls_resourcevsuser.csv",qoe_df)
        return qoe_df
        
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
        f'qoe_{client_id}': [qoe]
    })    
    
    # ? Record QoE Data
    write_or_append_csv(file_path,qoe_df)
    qoe_df['cpu'] = n_cpu_cores
    qoe_df['user'] = num_clients
    qoe_df['watch_time'] = watch_time
    write_or_append_csv("qoe_data_hls_resourcevsuser.csv",qoe_df)
    return qoe_df

  # TODO Create Convert to Pandas CSV
  
chrome_driver_path = '/opt/homebrew/bin/chromedriver'
def emulate_client(client_id,results):
    # Specify the path to the ChromeDriver


    # ? Random User Arrival
    time.sleep(initial_sleep_time)
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Set up the ChromeDriver service
    service = Service(chrome_driver_path)
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver = webdriver.Chrome(ChromeDriverManager().install()) #Use WebDriverManager Instead

    # driver.get(url_list[client_id])
    driver.get(url_list[3])
    # driver.get("http://127.0.0.1:8080/demo/index.html?src=http%3A%2F%2F192.168.50.54%3A30002%2Fhls%2Ftest.m3u8&demoConfig=eyJlbmFibGVTdHJlYW1pbmciOnRydWUsImF1dG9SZWNvdmVyRXJyb3IiOnRydWUsInN0b3BPblN0YWxsIjpmYWxzZSwiZHVtcGZNUDQiOmZhbHNlLCJsZXZlbENhcHBpbmciOi0xLCJsaW1pdE1ldHJpY3MiOi0xfQ==")
    

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
        
        # button = driver.find_element_by_name('config-apply')
        # button.click()        
        # Retrieve the metrics from the global variable
    jsonMetrics = driver.execute_script("""
        console.log(getMetrics());  // This will print the result to the browser's console
        return getMetrics();        // This returns the result to Python
    """)
    tend = driver.execute_script("return performance.now()-events.t0")
    
    # with open("sample.json", "w") as outfile:
    #     json.dump(jsonMetrics, outfile)
    print("Finished Running, Aggregating QoE Scores...")
    metrics = jsonMetrics
    _ = calculate_qoe(metrics, client_id, tend)
    driver.quit()

def main():
  while True:

    
    threads = []
    results = {}
    
    for i in range(num_clients):
        thread = threading.Thread(target=emulate_client, args=(i,results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    # Combine all results into a single DataFrame
    # combined_df = pd.DataFrame()
    # for i in range(num_clients):
    #     client_df = results[i].copy()
    #     print(client_df)
    #     if combined_df.empty:
    #         combined_df = client_df
    #     else:
    #         # combined_df = pd.merge(combined_df, client_df, on="Time", how="outer")
    #         combined_df = pd.concat([combined_df, client_df], axis=1)
    #         print(combined_df)
    # # Save the combined DataFrame to a CSV file
    # write_or_append_csv("QoE_test.csv", combined_df)
    # print("All QoE scores written to QoE_results.csv")

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
 