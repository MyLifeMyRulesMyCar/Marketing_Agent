"""
scheduler.py — Automated scheduler for Marketing Agents components.

Runs various data collection and processing tasks on schedules:
- RSS Feeder: Daily data collection
- Weekly digest: Weekly summary generation
- Serpi Feeder: Weekly Google Trends data
- Tavily Feeder: Weekly research data
- Reddit Watcher: Weekly Reddit scraping
- Vector DB: Weekly database updates

Usage:
    python scheduler.py              # Run scheduler (blocks)
    python scheduler.py --run-once   # Run all tasks once, then exit
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_command(command, cwd=None, description=""):
    """Run a command and return success status."""
    try:
        print(f"\n🔄 {description}")
        print(f"   Command: {command}")
        print(f"   CWD: {cwd or os.getcwd()}")

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed with code {result.returncode}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 1 hour")
        return False
    except Exception as e:
        print(f"💥 {description} failed with exception: {e}")
        return False

def run_rss_feeder():
    """Run RSS feeder daily data collection."""
    return run_command(
        "python main.py",
        cwd=PROJECT_ROOT / "RSS_Feeder",
        description="RSS Feeder daily collection"
    )

def run_weekly_digest():
    """Run weekly digest generation."""
    return run_command(
        "python weekly.py",
        cwd=PROJECT_ROOT / "RSS_Feeder",
        description="Weekly digest generation"
    )

def run_serpi_feeder():
    """Run Serpi feeder weekly Google Trends collection."""
    return run_command(
        "python main.py",
        cwd=PROJECT_ROOT / "Serpi_feeder",
        description="Serpi Feeder weekly trends"
    )

def run_tavily_feeder():
    """Run Tavily feeder weekly research collection."""
    return run_command(
        "python main.py",
        cwd=PROJECT_ROOT / "tavily_feeder",
        description="Tavily Feeder weekly research"
    )

def run_reddit_watcher():
    """Run Reddit watcher weekly scraping."""
    return run_command(
        "python main.py",
        cwd=PROJECT_ROOT / "reddit_watcher",
        description="Reddit Watcher weekly scraping"
    )

def run_vector_db_update():
    """Run vector database weekly update."""
    return run_command(
        "python make_vector_db.py",
        cwd=PROJECT_ROOT / "vector_db",
        description="Vector DB weekly update"
    )

def run_all_tasks_once():
    """Run all tasks once for testing."""
    print(f"\n🚀 Running all tasks once at {datetime.now()}")

    tasks = [
        ("RSS Feeder", run_rss_feeder),
        ("Weekly Digest", run_weekly_digest),
        ("Serpi Feeder", run_serpi_feeder),
        ("Tavily Feeder", run_tavily_feeder),
        ("Reddit Watcher", run_reddit_watcher),
        ("Vector DB Update", run_vector_db_update),
    ]

    results = {}
    for name, task_func in tasks:
        print(f"\n{'='*50}")
        success = task_func()
        results[name] = success

    print(f"\n{'='*50}")
    print("📊 Task Results Summary:")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {name}")

    successful = sum(results.values())
    total = len(results)
    print(f"\n🎯 {successful}/{total} tasks completed successfully")

    return successful == total

def main():
    parser = argparse.ArgumentParser(description="Marketing Agents Scheduler")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run all tasks once and exit (for testing)"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run the scheduler with predefined schedules"
    )

    args = parser.parse_args()

    if args.run_once:
        success = run_all_tasks_once()
        sys.exit(0 if success else 1)

    if args.schedule:
        try:
            import schedule
        except ImportError:
            print("❌ schedule library not found. Install with: pip install schedule")
            sys.exit(1)

        print("📅 Setting up automated schedules...")

        # Daily tasks
        schedule.every().day.at("06:00").do(run_rss_feeder)

        # Weekly tasks (Sunday at 7 AM)
        schedule.every().sunday.at("07:00").do(run_weekly_digest)
        schedule.every().sunday.at("08:00").do(run_serpi_feeder)
        schedule.every().sunday.at("09:00").do(run_tavily_feeder)
        schedule.every().sunday.at("10:00").do(run_reddit_watcher)
        schedule.every().sunday.at("11:00").do(run_vector_db_update)

        print("✅ Schedules configured:")
        print("   📆 Daily 6:00 AM: RSS Feeder")
        print("   📅 Sunday 7:00 AM: Weekly Digest")
        print("   📅 Sunday 8:00 AM: Serpi Feeder")
        print("   📅 Sunday 9:00 AM: Tavily Feeder")
        print("   📅 Sunday 10:00 AM: Reddit Watcher")
        print("   📅 Sunday 11:00 AM: Vector DB Update")
        print("\n🔄 Scheduler running... (Ctrl+C to stop)")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user")
            sys.exit(0)

    else:
        print("Usage:")
        print("  python scheduler.py --run-once    # Test all tasks")
        print("  python scheduler.py --schedule    # Run automated scheduler")
        sys.exit(1)

if __name__ == "__main__":
    main()