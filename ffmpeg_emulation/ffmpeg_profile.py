import subprocess
import psutil
import time
import threading
import re
import csv

ffmpeg_cmd = [
    "ffmpeg", "-re", "-stream_loop", "-1", "-t", "120",  # Run for 2 minutes
    "-i", "Big_Buck_Bunny.mp4",
    "-c:v", "libx264", "-preset", "fast", "-b:v", "800k",
    "-c:a", "aac", "-b:a", "128k",
    "-f", "null", "/dev/null"
]

# Regex to extract FFmpeg metricsff
progress_re = re.compile(r"frame=.*?fps=(.*?)\s+q=(.*?)\s+size=.*?time=(.*?)\s+bitrate=.*?speed=(.*?)x")

# Data containers
fps_samples = []
cpu_samples = []
mem_samples = []
q_samples = []
bitrate_samples = []
perf_output = ""

# Start FFmpeg
ffmpeg_proc = subprocess.Popen(
    ffmpeg_cmd,
    stderr=subprocess.PIPE,
    stdout=subprocess.DEVNULL,
    text=True
)
ffmpeg_pid = ffmpeg_proc.pid

def monitor_ffmpeg_logs():
    print("🔁 Monitoring FFmpeg logs...")
    for line in ffmpeg_proc.stderr:
        match = progress_re.search(line)
        if match:
            fps, q, t, speed = match.groups()

            fps = float(fps) if fps != "N/A" else 0
            q_val = float(q) if q != "N/A" else 0

            # Extract bitrate from the line using regex
            bitrate_match = re.search(r"bitrate=\s*([\d.]+)\s*kbits/s", line)
            bitrate = float(bitrate_match.group(1)) if bitrate_match else 0

            fps_samples.append(fps)
            q_samples.append(q_val)
            bitrate_samples.append(bitrate)

            print(f"[FFmpeg] fps={fps}, q={q}, bitrate={bitrate}, time={t}, speed={speed}x")

system_cpu_samples = []
system_mem_samples = []

def monitor_resources(pid):
    print("🧠 Monitoring process + system resource usage...")
    proc = psutil.Process(pid)
    while ffmpeg_proc.poll() is None:
        try:
            # Process-level
            cpu = proc.cpu_percent(interval=1)
            mem = proc.memory_info().rss / 1e6  # MB
            cpu_samples.append(cpu)
            mem_samples.append(mem)

            # System-level
            sys_cpu = psutil.cpu_percent(interval=None)
            sys_mem = psutil.virtual_memory().percent
            system_cpu_samples.append(sys_cpu)
            system_mem_samples.append(sys_mem)

        except psutil.NoSuchProcess:
            break

def run_perf(pid):
    global perf_output
    print("⚙️ Running perf stat...")
    perf_cmd = ["sudo", "perf", "stat", "-p", str(pid)]
    result = subprocess.run(perf_cmd, text=True, capture_output=True)
    perf_output = result.stderr

# Start monitoring threads
log_thread = threading.Thread(target=monitor_ffmpeg_logs)
resource_thread = threading.Thread(target=monitor_resources, args=(ffmpeg_pid,))
perf_thread = threading.Thread(target=run_perf, args=(ffmpeg_pid,))

log_thread.start()
resource_thread.start()
perf_thread.start()

log_thread.join()
resource_thread.join()
perf_thread.join()

print("✅ Monitoring finished.")

# ----------------------
# 🔍 Parse perf output
# ----------------------
def extract_perf_value(label):
    for line in perf_output.splitlines():
        if label in line:
            parts = line.strip().split()
            for val in parts:
                try:
                    return float(val.replace(',', ''))
                except ValueError:
                    continue
    return "N/A"

task_clock = extract_perf_value("task-clock")
ctx_switches = extract_perf_value("context-switches")
cpu_migrations = extract_perf_value("cpu-migrations")
page_faults = extract_perf_value("page-faults")

# ----------------------
# 🧮 Aggregate and Save
# ----------------------
avg_fps = sum(fps_samples) / len(fps_samples) if fps_samples else 0
avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
avg_mem = sum(mem_samples) / len(mem_samples) if mem_samples else 0
avg_q = sum(q_samples) / len(q_samples) if q_samples else 0
avg_bitrate = sum(bitrate_samples) / len(bitrate_samples) if bitrate_samples else 0
avg_sys_cpu = sum(system_cpu_samples) / len(system_cpu_samples) if system_cpu_samples else 0
avg_sys_mem = sum(system_mem_samples) / len(system_mem_samples) if system_mem_samples else 0

output_file = "ffmpeg_summary.csv"
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "task-clock(ms)", "context-switches", "cpu-migrations", "page-faults",
        "avg-fps", "avg-q", "avg-bitrate(kbits/s)",
        "avg-process-CPU(%)", "avg-process-Memory(MB)",
        "avg-system-CPU(%)", "avg-system-Memory(%)"
    ])
    writer.writerow([
        f"{task_clock}", f"{ctx_switches}", f"{cpu_migrations}", f"{page_faults}",
        f"{avg_fps:.2f}", f"{avg_q:.2f}", f"{avg_bitrate:.2f}",
        f"{avg_cpu:.2f}", f"{avg_mem:.2f}",
        f"{avg_sys_cpu:.2f}", f"{avg_sys_mem:.2f}"
    ])


print(f"✅ Summary written to {output_file}")
