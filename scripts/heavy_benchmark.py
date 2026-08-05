import time
import multiprocessing
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:8080"
CONCURRENT_REQUESTS = 50
TOTAL_REQUESTS_PER_PROCESS = 1000

def fetch(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except Exception:
        return 0

def run_load_test():
    print(f"[PID: {multiprocessing.current_process().pid}] Starting high-concurrency load test...")
    urls = [f"{BASE_URL}/api/ping", f"{BASE_URL}/api/config"] * (TOTAL_REQUESTS_PER_PROCESS // 2)
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        responses = list(executor.map(fetch, urls))
    end_time = time.time()
    
    success = sum(1 for r in responses if r == 200)
    print(f"[PID: {multiprocessing.current_process().pid}] Sent {len(responses)} requests in {end_time - start_time:.2f}s. Success: {success}")

def heavy_computation():
    # Force CPU usage
    for i in range(5000000):
        _ = math.sqrt(i) * math.sin(i)

def worker_process():
    # Run CPU intensive task to simulate complex agent routing/parsing
    heavy_computation()
    # Run Network intensive task to hammer the API
    run_load_test()

if __name__ == "__main__":
    print("🚀 [CRITICAL WORKLOAD] Launching Hyper-Concurrency Matrix...")
    cpu_cores = max(2, multiprocessing.cpu_count() - 1)
    processes = []
    
    for _ in range(cpu_cores):
        p = multiprocessing.Process(target=worker_process)
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
    print("✅ Hyper-Concurrency Matrix completed.")
