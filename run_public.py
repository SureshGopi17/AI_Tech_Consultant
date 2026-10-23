"""
Public Tunnel Runner for AI Tech Consultant Monorepo.
Launches all microservices and establishes public Cloudflare tunnels for:
- Master Control Portal (Port 8000)
- Task 1: The Knowledge Brain (Port 8001)
- Task 2: The Inbox Agent (Port 8002)
- Task 3: Meeting to Scope of Work (Port 8003)

Dynamically writes public URLs to portal/config.json and PUBLIC_URLS.md.
"""

import sys
import os
import re
import time
import json
import subprocess
import threading
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED = os.path.join(ROOT_DIR, "cloudflared.exe")

def start_portal_server(port=8000):
    portal_dir = os.path.join(ROOT_DIR, "portal")
    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=portal_dir, **kwargs)
        def log_message(self, format, *args):
            pass

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

def start_tunnel(port, captured_urls, tunnel_procs):
    cmd = [CLOUDFLARED, "tunnel", "--url", f"http://localhost:{port}"]
    proc = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    tunnel_procs.append((f"Tunnel-{port}", proc))

    def err_reader():
        found = False
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            if not found:
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    captured_urls[port] = m.group(0)
                    found = True

    def out_reader():
        while True:
            line = proc.stdout.readline()
            if not line:
                break

    t_err = threading.Thread(target=err_reader, daemon=True)
    t_err.start()
    t_out = threading.Thread(target=out_reader, daemon=True)
    t_out.start()

def main():
    print("\n" + "=" * 70)
    print("🌐 STARTING AI TECH CONSULTANT WITH LIVE PUBLIC CLOUDFLARE TUNNELS")
    print("=" * 70 + "\n")

    if not os.path.exists(CLOUDFLARED):
        print(f"❌ Error: cloudflared.exe not found at {CLOUDFLARED}")
        sys.exit(1)

    service_procs = []
    tunnel_procs = []

    try:
        # 1. Start Task 1: Knowledge Brain (Port 8001)
        print("▶ [1/4] Launching Task 1: The Knowledge Brain (FastAPI on port 8001)...")
        t1_dir = os.path.join(ROOT_DIR, "task1_knowledge_brain")
        p1 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"],
            cwd=t1_dir
        )
        service_procs.append(("Task 1 (Knowledge Brain)", p1))

        # 2. Start Task 2: Inbox Agent (Port 8002)
        print("▶ [2/4] Launching Task 2: The Inbox Agent (TypeScript on port 8002)...")
        t2_dir = os.path.join(ROOT_DIR, "task2_inbox_agent")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        p2 = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=t2_dir
        )
        service_procs.append(("Task 2 (Inbox Agent)", p2))

        # 3. Start Task 3: Meeting to SOW (Port 8003)
        print("▶ [3/4] Launching Task 3: Meeting to Scope of Work (FastAPI on port 8003)...")
        t3_dir = os.path.join(ROOT_DIR, "task3_meeting_sow")
        p3 = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"],
            cwd=t3_dir
        )
        service_procs.append(("Task 3 (Meeting to SOW)", p3))

        # 4. Start Unified Portal (Port 8000)
        print("▶ [4/4] Launching Unified Portal Dashboard (port 8000)...")
        start_portal_server(8000)

        # Health polling
        print("\n⏳ Verifying service health before opening public tunnels...")
        wait_for_health("http://localhost:8001/api/v1/health", label="Task 1")
        wait_for_health("http://localhost:8002/api/v1/health", label="Task 2")
        wait_for_health("http://localhost:8003/api/v1/health", label="Task 3")
        print("✅ All 4 local services healthy.\n")

        # Start 4 Cloudflare Tunnels
        print("🔗 Establishing Cloudflare Quick Tunnels for all services...")
        captured_urls = {}
        ports = [8000, 8001, 8002, 8003]
        for p in ports:
            start_tunnel(p, captured_urls, tunnel_procs)

        # Wait up to 30s for all 4 URLs
        start_time = time.time()
        while len(captured_urls) < 4 and time.time() - start_time < 30:
            time.sleep(0.5)

        if len(captured_urls) < 4:
            print(f"⚠️ Warning: Captured {len(captured_urls)}/4 tunnel URLs: {captured_urls}")
        else:
            print("✨ All 4 public tunnels established successfully!\n")

        portal_url = captured_urls.get(8000, "http://localhost:8000")
        t1_url = captured_urls.get(8001, "http://localhost:8001")
        t2_url = captured_urls.get(8002, "http://localhost:8002")
        t3_url = captured_urls.get(8003, "http://localhost:8003")

        # Update portal/config.json
        config_path = os.path.join(ROOT_DIR, "portal", "config.json")
        config_data = {
            "public_mode": True,
            "portal": portal_url,
            "task1": t1_url,
            "task2": t2_url,
            "task3": t3_url,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        # Write PUBLIC_URLS.md
        public_urls_path = os.path.join(ROOT_DIR, "PUBLIC_URLS.md")
        public_urls_content = f"""# AI Tech Consultant — Public Live URLs

This monorepo is currently live and accessible over the internet via secure HTTPS Cloudflare Tunnels.
External reviewers, evaluators, and stakeholders can click the links below directly to access every service.

---

## 🚀 Live Access Directory

| Component | Description | Live Public URL | Local Port |
| :--- | :--- | :--- | :--- |
| **Unified Portal** | Master Dashboard & Architecture Flow | [{portal_url}]({portal_url}) | `8000` |
| **Task 1: Knowledge Brain** | Brilliant Directories RAG & Escalations | [{t1_url}]({t1_url}) | `8001` |
| **Task 1 OpenAPI Docs** | Interactive Swagger API Explorer | [{t1_url}/docs]({t1_url}/docs) | `8001` |
| **Task 2: Inbox Agent** | Strict TypeScript Email Drafter & Graduation | [{t2_url}]({t2_url}) | `8002` |
| **Task 3: Meeting to SOW** | Multi-Agent Transcript Analyzer & SOW | [{t3_url}]({t3_url}) | `8003` |
| **Task 3 OpenAPI Docs** | Interactive Swagger API Explorer | [{t3_url}/docs]({t3_url}/docs) | `8003` |

---

## ⚡ Quick Test Commands (cURL)

Verify the live endpoints from any external machine or terminal:

```bash
# 1. Test Task 1 Health Check
curl -s {t1_url}/api/v1/health

# 2. Query Knowledge Brain
curl -s -X POST {t1_url}/api/v1/search -H "Content-Type: application/json" -d "{{\\"query\\":\\"How do I configure QuickBooks integration?\\"}}"

# 3. Test Task 2 Inbox Agent Emails
curl -s {t2_url}/api/v1/emails

# 4. Test Task 3 Meeting Transcripts
curl -s {t3_url}/api/v1/transcripts/meeting_1
```

---
*Generated by `run_public.py` on {time.strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
        with open(public_urls_path, "w", encoding="utf-8") as f:
            f.write(public_urls_content)

        print("=" * 70)
        print("🌟 AI TECH CONSULTANT IS LIVE ON THE PUBLIC WEB!")
        print("=" * 70)
        print(f"  • MASTER PORTAL:       {portal_url}")
        print(f"  • Task 1 Brain UI:     {t1_url}  (Docs: {t1_url}/docs)")
        print(f"  • Task 2 Inbox UI:     {t2_url}")
        print(f"  • Task 3 SOW UI:       {t3_url}  (Docs: {t3_url}/docs)")
        print("=" * 70)
        print("📁 Public URLs saved to: PUBLIC_URLS.md and portal/config.json")
        print("Press Ctrl+C at any time to gracefully terminate all tunnels and services.\n")

        # Keep alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all public tunnels and services gracefully...")
        for name, proc in tunnel_procs:
            proc.terminate()
        for name, proc in service_procs:
            proc.terminate()
        for _, proc in tunnel_procs:
            proc.wait()
        for _, proc in service_procs:
            proc.wait()
        print("✅ All tunnels and services shut down.")

if __name__ == "__main__":
    main()
