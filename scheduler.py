"""
scheduler.py — Marketing Agents Automated Scheduler
Runs daily between 8PM-9PM window. Week starts Monday.

Fixes:
  - Windows cp1252 emoji crash → forces UTF-8 encoding on all subprocesses
  - .env files in subfolders → loaded explicitly before each task

Usage:
  python scheduler.py             # start the scheduler (runs forever)
  python scheduler.py --run-once  # run everything once right now (for testing)
  python scheduler.py --status    # show next scheduled run times
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import schedule

PROJECT_ROOT = Path(__file__).parent
LOG_FILE     = PROJECT_ROOT / "scheduler_log.txt"


# ── Logging ───────────────────────────────────────────────────

def log(msg: str):
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    # stdout: replace unencodable chars so the terminal never crashes
    print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Env loader ────────────────────────────────────────────────

def load_env_for(subfolder: str):
    """Load the .env file from a subfolder into the current process."""
    env_path = PROJECT_ROOT / subfolder / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)


# ── Task runner ───────────────────────────────────────────────

def run_task(name: str, command: str, cwd: Path, env_subfolder: str = None) -> bool:
    log(f"[START] {name}")
    start = datetime.now()

    # Build environment: inherit current env + force UTF-8
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"]       = "1"

    # Load the component's .env into the subprocess environment
    if env_subfolder:
        env_path = PROJECT_ROOT / env_subfolder / ".env"
        if env_path.exists():
            # Parse the .env manually and inject into env dict
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        if key and val:
                            env[key] = val

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,
            env=env,
        )
        elapsed = (datetime.now() - start).seconds

        if result.returncode == 0:
            log(f"[OK]     {name} ({elapsed}s)")
            lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
            for line in lines[-5:]:
                log(f"         {line}")
            return True
        else:
            log(f"[FAIL]   {name} (exit {result.returncode}, {elapsed}s)")
            stderr_lines = (result.stderr or "").strip().splitlines()
            for line in stderr_lines[-5:]:
                log(f"         {line}")
            return False

    except subprocess.TimeoutExpired:
        log(f"[TIMEOUT] {name} (over 1 hour)")
        return False
    except Exception as e:
        log(f"[ERROR]  {name}: {e}")
        return False


# ── Individual tasks ──────────────────────────────────────────

def task_rss_feeder():
    run_task(
        "RSS Feeder — daily collect",
        "python main.py",
        PROJECT_ROOT / "RSS_Feeder",
    )

def task_weekly_digest():
    run_task(
        "Weekly Digest — top articles",
        "python weekly.py",
        PROJECT_ROOT / "RSS_Feeder",
    )

def task_serpi_feeder():
    run_task(
        "Serpi Feeder — Google Trends",
        "python main.py --profile standard",
        PROJECT_ROOT / "Serpi_feeder",
        env_subfolder="Serpi_feeder",
    )

def task_tavily_feeder():
    run_task(
        "Tavily Feeder — competitor research",
        "python main.py",
        PROJECT_ROOT / "tavily_feeder",
        env_subfolder="tavily_feeder",
    )

def task_reddit_watcher():
    run_task(
        "Reddit Watcher — subreddit scraping",
        "python main.py --sort top --time week",
        PROJECT_ROOT / "reddit_watcher",
        env_subfolder="reddit_watcher",
    )

def task_vector_db():
    run_task(
        "Vector DB — update index",
        "python make_vector_db.py",
        PROJECT_ROOT / "vector_db",
    )


# ── Pre-flight check ──────────────────────────────────────────

def preflight_check():
    log("Pre-flight check...")
    checks = [
        ("Serpi_feeder",    "SERPAPI_KEY"),
        ("tavily_feeder",   "TAVILY_API_KEY"),
        ("reddit_watcher",  "REDDIT_CLIENT_ID"),
        ("reddit_watcher",  "REDDIT_CLIENT_SECRET"),
    ]
    all_ok = True
    for subfolder, var in checks:
        env_path = PROJECT_ROOT / subfolder / ".env"
        found = False
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(var + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            found = True
                            break
        status = "OK" if found else "MISSING"
        if not found:
            all_ok = False
        log(f"   [{status}] {subfolder}/.env -> {var}")

    if all_ok:
        log("All credentials found.")
    else:
        log("WARNING: Some credentials missing — those tasks will fail.")
    return all_ok


# ── Schedule setup ────────────────────────────────────────────

def setup_schedules():
    schedule.every().day.at("20:00").do(task_rss_feeder)
    schedule.every().monday.at("20:05").do(task_weekly_digest)
    schedule.every().monday.at("20:15").do(task_serpi_feeder)
    schedule.every().monday.at("20:25").do(task_tavily_feeder)
    schedule.every().monday.at("20:35").do(task_reddit_watcher)
    schedule.every().monday.at("20:50").do(task_vector_db)

    log("Schedules set:")
    log("   Daily   20:00  RSS Feeder")
    log("   Monday  20:05  Weekly Digest")
    log("   Monday  20:15  Serpi Feeder")
    log("   Monday  20:25  Tavily Feeder")
    log("   Monday  20:35  Reddit Watcher")
    log("   Monday  20:50  Vector DB Update")


# ── CLI modes ─────────────────────────────────────────────────

def show_status():
    setup_schedules()
    print(f"\n{'='*55}")
    print(" Next scheduled runs:")
    print(f"{'='*55}")
    for job in schedule.jobs:
        next_run = job.next_run.strftime("%Y-%m-%d %H:%M") if job.next_run else "?"
        print(f"  {next_run}  ->  {job.job_func.__name__}")
    print(f"{'='*55}\n")


def run_all_once():
    log("Running all tasks once (test mode)")
    log("=" * 55)
    tasks = [
        task_rss_feeder,
        task_weekly_digest,
        task_serpi_feeder,
        task_tavily_feeder,
        task_reddit_watcher,
        task_vector_db,
    ]
    for fn in tasks:
        log(f"\n{'─'*40}")
        fn()
    log(f"\n{'='*55}")
    log(f"Test run complete — {len(tasks)} tasks executed")


def main():
    parser = argparse.ArgumentParser(description="Marketing Agents Scheduler")
    parser.add_argument("--run-once", action="store_true", help="Run all tasks once and exit")
    parser.add_argument("--status",   action="store_true", help="Show next run times and exit")
    args = parser.parse_args()

    if args.run_once:
        preflight_check()
        run_all_once()
        return

    if args.status:
        show_status()
        return

    # Normal mode
    log("=" * 55)
    log("Marketing Agents Scheduler — starting")
    log("=" * 55)
    log(f"Project root : {PROJECT_ROOT}")
    log(f"Log file     : {LOG_FILE}")
    log(f"Start time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    preflight_check()
    setup_schedules()
    log("Scheduler running. Press Ctrl+C to stop.\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        log("Scheduler stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()