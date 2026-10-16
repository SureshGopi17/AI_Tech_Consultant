"""
Master Runner for AI Tech Consultant Monorepo.
Runs all three tasks and the master portal with one command:
- Task 1: Knowledge Brain (FastAPI on Port 8001)
- Task 2: Inbox Agent (TypeScript Express on Port 8002)
- Task 3: Meeting to Scope of Work (FastAPI on Port 8003)
- Portal: Unified Dashboard on Port 8000
"""

import sys
import os
import time
import subprocess
import signal
import urllib.request
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def start_portal_server(port=8000):
    portal_dir = os.path.join(ROOT_DIR, "portal")
    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=portal_dir, **kwargs)
        def log_message(self, format, *args):
            pass # suppress verbose access logs

    httpd = HTTPServer(("0.0.0.0", port), CustomHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd

def wait_for_health(url, timeout=30, label="Service"):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def main():
    print("\n" + "=" * 65)
    print("🚀 STARTING AI TECH CONSULTANT MONOREPO (ONE-COMMAND RUN)")
    print("=" * 65 + "\n")

    processes = []

    try:
        # 1. Start Task 1: Knowledge Brain (Port 8001)
        print("▶ [1/4] Launching Task 1: The Knowledge Brain (Python FastAPI on port 8001)...")
        t1_dir = os.path.join(ROOT_DIR, "task1_knowledge_brain")
        p1 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
            cwd=t1_dir
        )
        processes.append(("Task 1 (Knowledge Brain)", p1))

        # 2. Start Task 2: Inbox Agent (Port 8002)
        print("▶ [2/4] Launching Task 2: The Inbox Agent (TypeScript on port 8002)...")
        t2_dir = os.path.join(ROOT_DIR, "task2_inbox_agent")
        # Use npx tsx src/server.ts or npm start
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        p2 = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=t2_dir
        )
        processes.append(("Task 2 (Inbox Agent)", p2))

        # 3. Start Task 3: Meeting to SOW (Port 8003)
        print("▶ [3/4] Launching Task 3: Meeting to Scope of Work (Python FastAPI on port 8003)...")
        t3_dir = os.path.join(ROOT_DIR, "task3_meeting_sow")
        p3 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"],
            cwd=t3_dir
        )
        processes.append(("Task 3 (Meeting to SOW)", p3))

        # 4. Start Unified Portal (Port 8000)
        print("▶ [4/4] Launching Unified Portal Dashboard (port 8000)...")
        start_portal_server(8000)

        # Health polling
        print("\n⏳ Verifying service health status...")
        t1_ok = wait_for_health("http://localhost:8001/api/v1/health", label="Task 1")
        t2_ok = wait_for_health("http://localhost:8002/api/v1/health", label="Task 2")
        t3_ok = wait_for_health("http://localhost:8003/api/v1/health", label="Task 3")

        print("\n" + "=" * 65)
        print("✨ ALL THREE SERVICES ARE LIVE AND OPERATIONAL!")
        print("=" * 65)
        print(f"  • Master Portal:       http://localhost:8000")
        print(f"  • Task 1 Brain UI:     http://localhost:8001  (OpenAPI: /docs)")
        print(f"  • Task 2 Inbox UI:     http://localhost:8002")
        print(f"  • Task 3 SOW UI:       http://localhost:8003  (OpenAPI: /docs)")
        print("=" * 65)
        print("Press Ctrl+C at any time to gracefully terminate all services.\n")

        # Keep parent alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all AI Tech Consultant services gracefully...")
        for name, proc in processes:
            print(f"  Terminating {name}...")
            proc.terminate()
        for name, proc in processes:
            proc.wait()
        print("✅ All services shut down successfully.")

if __name__ == "__main__":
    main()
