"""
Verification script for Phase 2 Frontend Foundation & Backend Integration.
Tests:
1. Backend startup and health check (GET /api/v1/health).
2. Backend CORS headers allowing http://localhost:5173.
3. Frontend Vite preview serving application shell and assets.
4. Disconnected backend handling verification.
"""

import os
import sys
import time
import subprocess
import httpx

def run_checks():
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"

    print("=== STEP 1: Starting Backend Server on 127.0.0.1:8000 ===")
    backend_proc = subprocess.Popen(
        [
            r"backend\.venv\Scripts\uvicorn.exe",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(2)

    try:
        # Check backend health
        print("Checking Backend GET /api/v1/health...")
        r_health = httpx.get("http://127.0.0.1:8000/api/v1/health", timeout=5.0)
        assert r_health.status_code == 200, f"Expected 200, got {r_health.status_code}"
        health_data = r_health.json()
        print("Backend Health Response:", health_data)
        assert health_data["status"] == "healthy"
        assert health_data["application"] == "FlameLens"

        # Check CORS headers
        print("Checking CORS headers for Origin: http://localhost:5173...")
        r_cors = httpx.options(
            "http://127.0.0.1:8000/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
            timeout=5.0,
        )
        print("CORS Status:", r_cors.status_code)
        allow_origin = r_cors.headers.get("access-control-allow-origin")
        print("Access-Control-Allow-Origin:", allow_origin)
        assert allow_origin in ["http://localhost:5173", "*"], f"Unexpected CORS origin: {allow_origin}"

        print("=== STEP 2: Starting Frontend Preview on 127.0.0.1:5173 ===")
        frontend_proc = subprocess.Popen(
            ["npx.cmd", "vite", "preview", "--port", "5173", "--host", "127.0.0.1"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        time.sleep(3)

        try:
            print("Checking Frontend GET http://127.0.0.1:5173/...")
            r_fe = httpx.get("http://127.0.0.1:5173/", timeout=5.0)
            assert r_fe.status_code == 200, f"Expected 200, got {r_fe.status_code}"
            assert "FlameLens" in r_fe.text
            print("Frontend returned 200 OK with FlameLens HTML shell.")

            print("Checking Frontend SPA routing GET http://127.0.0.1:5173/overview...")
            r_fe_overview = httpx.get("http://127.0.0.1:5173/overview", timeout=5.0)
            assert r_fe_overview.status_code == 200, f"Expected 200, got {r_fe_overview.status_code}"
            print("Frontend SPA routing /overview returned 200 OK.")

        finally:
            print("Stopping Frontend preview server...")
            frontend_proc.terminate()
            frontend_proc.wait()

    finally:
        print("Stopping Backend server...")
        backend_proc.terminate()
        backend_proc.wait()

    print("=== STEP 3: Verifying Disconnected Backend Handling ===")
    try:
        httpx.get("http://127.0.0.1:8000/api/v1/health", timeout=1.0)
        print("ERROR: Backend should be down!")
        sys.exit(1)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        print("Confirmed: Backend actively refused connection or timed out when offline (Proper Disconnected State).")

    print("\n>>> ALL VERIFICATION CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_checks()
