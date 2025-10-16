import subprocess
import psutil
import threading
import re
import csv
import argparse
import os
import time
import random
# sudo python3 multi_ffmpeg_profile.py --resolution 1080p --num_tasks 3

# -------- Command-line Argument Parsing --------
parser = argparse.ArgumentParser(description="Run multiple FFmpeg tasks and monitor performance.")
parser.add_argument("--resolution", choices=["480p", "720p", "1080p"], default="1080p", help="Set video resolution")
parser.add_argument("--num_tasks", type=int, default=2, help="Number of parallel FFmpeg tasks to run")
parser.add_argument("--execution_time", type=int, default=120, help="FFMPEG Execution Time")
args = parser.parse_args()

# -------- Resolution Mapping --------
resolution_map = {
    "480p": '-vf scale=854:480 -b:a 128k -f null /dev/null', #-b:v 800k
    "720p": '-vf scale=1280:720 -b:a 128k -f null /dev/null', #-b:v 2500k
    "1080p": '-vf scale=1920:1080 -b:a 128k -f null /dev/null' #-b:v 4500k
}
RESOLUTION = resolution_map[args.resolution]
NUM_INSTANCES = args.num_tasks  # Modify this to run more FFmpeg instances
EXECUTION_TIME = args.execution_time
# -------- Regex --------
progress_re = re.compile(r"frame=.*?fps=(.*?)\s+q=(.*?)\s+size=.*?time=(.*?)\s+bitrate=.*?speed=(.*?)x")

# ----------------------
# 🔧 Monitoring Function per Instance
# ----------------------
def run_ffmpeg_instance(index):
    base_cmd = [
        "ffmpeg", "-ss", str(random.randint(0,360)),
        # "-re", 
        "-stream_loop", "-1", "-t", f"{EXECUTION_TIME}",
        "-i", "Bunny_30fps.mp4",
        "-c:v", "libx264", "-preset", "superfast",
        "-c:a", "aac", "-qp", "23",
    ]
    # ffmpeg_cmd = [
    #     "ffmpeg", "-re", "-stream_loop", "-1", "-t", "120",
    #     "-i", "Big_Buck_Bunny.mp4",
    #     "-c:v", "libx264", "-preset", "fast", "-b:v", "800k",
    #     "-c:a", "aac", "-b:a", "128k",
    #     "-f", "null", "/dev/null"
    # ]    

    # Split the string from the map into list args
    resolution_args = resolution_map[args.resolution].split()
    ffmpeg_cmd = base_cmd + resolution_args

    fps_samples, q_samples, bitrate_samples = [], [], []
    cpu_samples, mem_samples = [], []
    sys_cpu_samples, sys_mem_samples = [], []
    perf_output = ""

    proc = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    pid = proc.pid
    ps_proc = psutil.Process(pid)

    def monitor_logs():
        for line in proc.stderr:
            if "frame=" in line:
                match = progress_re.search(line)
                if match:
                    fps, q, t, speed = match.groups()
                    fps_samples.append(float(fps) if fps != "N/A" else 0)
                    q_samples.append(float(q) if q != "N/A" else 0)
                    bitrate_match = re.search(r"bitrate=\s*([\d.]+)\s*kbits/s", line)
                    bitrate = float(bitrate_match.group(1)) if bitrate_match else 0
                    bitrate_samples.append(bitrate)
                    # time.sleep(1)
                    # print(f"[FFmpeg] fps={fps}, q={q}, bitrate={bitrate}, time={t}, speed={speed}x")

    def monitor_resources():
        while proc.poll() is None:
            try:
                cpu = ps_proc.cpu_percent(interval=1)
                mem = ps_proc.memory_info().rss / 1e6
                sys_cpu = psutil.cpu_percent(interval=None)
                sys_mem = psutil.virtual_memory().percent

                cpu_samples.append(cpu)
                mem_samples.append(mem)
                sys_cpu_samples.append(sys_cpu)
                sys_mem_samples.append(sys_mem)
                # time.sleep(1)
            except psutil.NoSuchProcess:
                break

    def run_perf_and_timer_interrupt():
        nonlocal perf_output
        perf_cmd = ["sudo", "perf", "stat", "-p", str(pid)]
        
        # Start perf as a subprocess — not blocking
        perf_proc = subprocess.Popen(perf_cmd, text=True, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL)

        # # Sleep for the max allowed execution time
        # time.sleep(EXECUTION_TIME + 5)
        
        # # if proc.poll() is None:
        # #     return
        # print("⏰ Time limit reached. Terminating FFmpeg process.")
        # try:
        #     proc.terminate()
        #     # proc.wait(timeout=5)
        # except Exception as e:
        #     print(f"⚠️ Could not terminate FFmpeg cleanly: {e}")
        #     proc.kill()

        # Collect perf output after FFmpeg is killed
        # try:
        #     perf_output = perf_proc.communicate(timeout=3)[1]
        #     print("=====Perf Output=====\n", perf_output)
        # except Exception as e:
        #     print(f"⚠️ Failed to get perf output: {e}")
        #     perf_proc.kill()
        
        try:
            # Wait for the main monitored process to finish
            proc.wait()

            # Then terminate perf
            perf_proc.terminate()

            # Collect perf output
            perf_output = perf_proc.communicate(timeout=3)[1]
            print("=====Perf Output=====\n", perf_output)

        except Exception as e:
            print(f"⚠️ Failed to complete perf monitoring cleanly: {e}")
            perf_proc.kill()  
   
        

    # Start threads
    t1 = threading.Thread(target=monitor_logs)
    t2 = threading.Thread(target=monitor_resources)
    t3 = threading.Thread(target=run_perf_and_timer_interrupt)
    
    start = time.time()
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    def extract_perf_value(label):
        for line in perf_output.splitlines():
            if label in line:
                parts = line.strip().split()
                for val in parts:
                    try:
                        return float(val.replace(',', ''))
                    except ValueError:
                        continue

        
        return 0
    
    
    task_clock = extract_perf_value("task-clock")
    ctx_switches = extract_perf_value("context-switches")
    cpu_migrations = extract_perf_value("cpu-migrations")
    page_faults = extract_perf_value("page-faults")
    perf_time_elapsed = extract_perf_value("seconds time elapsed")

    avg_fps = sum(fps_samples) / len(fps_samples) if fps_samples else 0
    avg_q = sum(q_samples) / len(q_samples) if q_samples else 0
    avg_bitrate = sum(bitrate_samples) / len(bitrate_samples) if bitrate_samples else 0
    avg_proc_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    avg_proc_mem = sum(mem_samples) / len(mem_samples) if mem_samples else 0
    avg_sys_cpu = sum(sys_cpu_samples) / len(sys_cpu_samples) if sys_cpu_samples else 0
    avg_sys_mem = sum(sys_mem_samples) / len(sys_mem_samples) if sys_mem_samples else 0
    frame_generated = min(avg_fps * perf_time_elapsed, EXECUTION_TIME * 30)

    # === Sanity Check for Failed Process ===
    # If output FPS is too low compared to expected total frames, mark it as failed
    expected_total_frames = EXECUTION_TIME * 30
    actual_total_frames = avg_fps * perf_time_elapsed

    # Assume failure if too few frames produced
    if actual_total_frames < 0.95 * expected_total_frames:  # you can adjust threshold
        print("Process Failed")
        avg_fps = avg_fps * actual_total_frames / expected_total_frames
        # perf_time_elapsed = expected_total_frames / 30  # fallback = EXECUTION_TIME

    print("== FPS Samples ==")
    print(actual_total_frames, expected_total_frames)
    if len(fps_samples): print(avg_fps)
    else: print(0)               
    
    
    return {
        "task_clock": task_clock,
        "ctx_switches": ctx_switches,
        "cpu_migrations": cpu_migrations,
        "page_faults": page_faults,
        "perf_time_elapsed": perf_time_elapsed,
        "avg_fps": avg_fps,
        "avg_q": avg_q,
        "avg_bitrate": avg_bitrate,
        "avg_proc_cpu": avg_proc_cpu,
        "avg_proc_mem": avg_proc_mem,
        "avg_sys_cpu": avg_sys_cpu,
        "avg_sys_mem": avg_sys_mem,
        "frame_generated": frame_generated,
    }

# ----------------------
# 🧮 Aggregate Across All Instances
# ----------------------
results = []
threads = []

def run_and_store(index):
    print(f"🚀 Running FFmpeg instance {index+1}")
    res = run_ffmpeg_instance(index)
    results.append(res)

start_time = time.time()
for i in range(NUM_INSTANCES):
    t = threading.Thread(target=run_and_store, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
    
    
time_elapsed = time.time() - start_time
def avg_of(key):
    return sum(r[key] for r in results) / len(results) if results else 0
def avg_of_n_task(key):
    return sum(r[key] for r in results) / len(results) if results else 0
def sum_of(key):
    return sum(r[key] for r in results)
# ----------------------
# 💾 Write to CSV
# ----------------------
output_file = "ffmpeg_summary_v2.csv"
file_exists = os.path.exists(output_file)

with open(output_file, "a" if file_exists else "w", newline="") as f:
    writer = csv.writer(f)

    if not file_exists:
        writer.writerow(["num_task", "cpu-allocated", "memory-allocated", "resolution", "time-elapsed",
            "task-clock(ms)", "context-switches", "cpu-migrations", "page-faults",
            "avg-fps", "avg-q", "avg-bitrate(kbits/s)",
            "avg-process-CPU(%)", "avg-process-Memory(MB)",
            "avg-system-CPU(%)", "avg-system-Memory(%)", "frame_generated"
        ])

    writer.writerow([ f"{args.num_tasks}", f"{psutil.cpu_count(logical=False)}", f"{psutil.virtual_memory().total}", f"{args.resolution[:-1]}", f"{avg_of_n_task('perf_time_elapsed'):.2f}",
        f"{avg_of_n_task('task_clock'):.2f}", f"{avg_of_n_task('ctx_switches'):.2f}", f"{avg_of_n_task('cpu_migrations'):.2f}", f"{avg_of_n_task('page_faults'):.2f}",
        f"{avg_of_n_task('avg_fps'):.2f}", f"{avg_of_n_task('avg_q'):.2f}", f"{avg_of_n_task('avg_bitrate'):.2f}",
        f"{avg_of_n_task('avg_proc_cpu'):.2f}", f"{avg_of_n_task('avg_proc_mem'):.2f}",
        f"{avg_of('avg_sys_cpu'):.2f}", f"{avg_of('avg_sys_mem'):.2f}", 
        f"{avg_of_n_task('frame_generated')}"
    ])

print(f"✅ All instances complete. Summary written to {output_file}")