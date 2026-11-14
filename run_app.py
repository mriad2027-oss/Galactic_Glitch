"""
TerraTwin AI - Unified Application Launcher
Starts both the FastAPI Backend (:8000) and Frontend Server (:8080) in one command,
monitors their health, and handles clean shutdown on Ctrl+C.
"""

import sys
import time
import subprocess
import webbrowser
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent

def main():
    print("=" * 65)
    print("           TERRATWIN AI - COMPLETE SYSTEM LAUNCHER")
    print("=" * 65)
    print("\n[1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.api.app:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=WORKSPACE
    )

    print("[2/3] Starting Frontend Server on http://localhost:8080 ...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd=WORKSPACE
    )

    time.sleep(2)
    print("[3/3] Opening browser at http://localhost:8080 ...")
    try:
        webbrowser.open("http://localhost:8080")
    except Exception:
        pass

    print("\n" + "=" * 65)
    print("  -> Frontend: http://localhost:8080")
    print("  -> Backend API: http://127.0.0.1:8000")
    print("  -> API Docs: http://127.0.0.1:8000/docs")
    print("=" * 65)
    print("\nPress Ctrl+C at any time to shut down both servers cleanly.\n")

    try:
        while True:
            # Check if either process died unexpectedly
            if backend_proc.poll() is not None:
                print(f"[ERROR] Backend exited with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                print(f"[ERROR] Frontend exited with code {frontend_proc.returncode}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping TerraTwin servers...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        try:
            backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()
        try:
            frontend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()
        print("[SHUTDOWN] Both servers stopped cleanly.")

if __name__ == "__main__":
    main()
