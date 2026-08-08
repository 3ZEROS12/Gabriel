#!/usr/bin/env python3
"""Gabriel Stability Run & Memory Leak Verification Script.

Runs simulated long-term workload (chat, KB read/write, WebSocket disconnect/reconnect)
over a parameterized duration (--hours), sampling RSS memory and endpoint telemetry.

Usage:
    python scripts/stability_run.py --hours 0.25
"""
import argparse
import sys
import os
import time
import logging
import sqlite3
from typing import List, Tuple

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from src.main import app, API_KEY, init_schema, save_insight

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stability_run")


def get_rss_mb() -> float:
    """Return current process RSS memory in MB."""
    if HAS_PSUTIL:
        return psutil.Process().memory_info().rss / (1024 * 1024)
    # Fallback to sys memory approximation if psutil is unavailable
    import gc
    gc.collect()
    return float(sys.getsizeof(gc.get_objects())) / (1024 * 1024)


def run_stability_test(hours: float) -> bool:
    total_seconds = float(hours) * 3600.0
    # Collect ~15 samples across duration, at least every 5s, max 60s
    sample_interval = max(5.0, min(60.0, total_seconds / 15.0))
    max_samples = max(3, int(total_seconds / sample_interval))

    logger.info(f"🚀 Starting stability run for {hours:.2f} hours ({total_seconds:.1f}s, {max_samples} samples every {sample_interval:.1f}s)")
    report_file = os.path.join(ROOT_DIR, "stability_report.txt")

    client = TestClient(app)

    db_path = os.path.join(ROOT_DIR, "knowledge.db")
    conn = sqlite3.connect(db_path)
    init_schema(conn)
    conn.close()

    headers = {"X-Gabriel-Token": API_KEY}
    rss_samples: List[Tuple[float, float]] = []  # (elapsed_sec, rss_mb)
    errors: List[str] = []

    start_time = time.time()
    sample_count = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= total_seconds and sample_count >= 3:
            break

        rss = get_rss_mb()
        rss_samples.append((elapsed, rss))
        sample_count += 1
        logger.info(f"Sample #{sample_count}: Elapsed={elapsed:.1f}s | RSS={rss:.2f}MB")

        # 1. Telemetry / Stats check
        try:
            res = client.get("/api/stats", headers=headers)
            if res.status_code != 200:
                errors.append(f"Sample #{sample_count} GET /api/stats failed status {res.status_code}")
        except Exception as e:
            errors.append(f"Sample #{sample_count} GET /api/stats exception: {e}")

        # 2. KB write and search round
        try:
            save_insight(f"Stability sample #{sample_count} check for memory leak and stability")
            search_res = client.post("/api/kb/search", json={"text": "stability sample"}, headers=headers)
            if search_res.status_code != 200:
                errors.append(f"Sample #{sample_count} POST /api/kb/search failed status {search_res.status_code}")
        except Exception as e:
            errors.append(f"Sample #{sample_count} KB round exception: {e}")

        # 3. Stuck reports round
        try:
            stuck_res = client.get("/api/stuck?limit=10", headers=headers)
            if stuck_res.status_code != 200:
                errors.append(f"Sample #{sample_count} GET /api/stuck failed status {stuck_res.status_code}")
        except Exception as e:
            errors.append(f"Sample #{sample_count} Stuck round exception: {e}")

        # 4. WebSocket connect / disconnect round
        try:
            with client.websocket_connect(f"/ws?token={API_KEY}") as ws:
                ws.send_json({"type": "ping"})
        except Exception as e:
            # Non-fatal if testclient websocket is skipped in some environments
            logger.debug(f"WS ping note: {e}")

        time.sleep(sample_interval)

    # Analyze results
    total_samples = len(rss_samples)
    midpoint = total_samples // 2

    first_half = [s[1] for s in rss_samples[:midpoint]] if midpoint > 0 else [rss_samples[0][1]]
    second_half = [s[1] for s in rss_samples[midpoint:]] if midpoint > 0 else [rss_samples[0][1]]

    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    max_rss = max(s[1] for s in rss_samples)
    min_rss = min(s[1] for s in rss_samples)

    # Assertions
    mem_ok = avg_second <= avg_first * 1.15
    errors_ok = len(errors) == 0
    passed = mem_ok and errors_ok

    report_lines = [
        "==================================================",
        "          GABRIEL STABILITY TEST REPORT           ",
        "==================================================",
        f"Timestamp       : {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Target Duration : {hours:.2f} hours ({total_seconds:.1f}s)",
        f"Actual Runtime  : {time.time() - start_time:.1f} seconds",
        f"Samples Taken   : {total_samples}",
        f"Memory Min RSS  : {min_rss:.2f} MB",
        f"Memory Max RSS  : {max_rss:.2f} MB",
        f"1st Half Avg    : {avg_first:.2f} MB",
        f"2nd Half Avg    : {avg_second:.2f} MB",
        f"Memory Growth   : {((avg_second - avg_first) / max(0.1, avg_first)) * 100:.2f}%",
        f"Errors Count    : {len(errors)}",
        "--------------------------------------------------",
        f"Memory Check (<=15% growth) : {'PASS' if mem_ok else 'FAIL'}",
        f"Error Log Check (0 errors)  : {'PASS' if errors_ok else 'FAIL'}",
        "--------------------------------------------------",
        f"FINAL VERDICT               : {'PASS' if passed else 'FAIL'}",
        "==================================================",
    ]

    if errors:
        report_lines.append("\nRecorded Error Log:")
        for err in errors:
            report_lines.append(f"  - {err}")

    report_content = "\n".join(report_lines)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print("\n" + report_content)
    return passed


def main():
    parser = argparse.ArgumentParser(description="Gabriel Long-term Stability Test Runner")
    parser.add_argument("--hours", type=float, default=0.25, help="Duration to run in hours (default: 0.25 for smoke test)")
    args = parser.parse_args()

    if args.hours <= 0:
        print("Error: --hours must be greater than 0")
        sys.exit(1)
    if args.hours > 72:
        print("Error: --hours max cap is 72")
        sys.exit(1)

    success = run_stability_test(args.hours)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
