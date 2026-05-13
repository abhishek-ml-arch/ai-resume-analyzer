#!/usr/bin/env python3
"""
AI Resume Analyzer - Single Command Launcher
Manages its own Python virtual environment and starts all services.
Press Ctrl+C to stop everything cleanly.
"""

import sys
import subprocess
import time
import signal
import os
from pathlib import Path

# Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
CYAN = "\033[96m"


def log(msg: str, color: str = RESET):
    print(f"{color}{msg}{RESET}")


def log_header(msg: str):
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}{msg}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")


def log_step(msg: str):
    print(f"{CYAN}[*] {msg}{RESET}")


def log_success(msg: str):
    print(f"{GREEN}[✓] {msg}{RESET}")


def log_error(msg: str):
    print(f"{RED}[✗] {msg}{RESET}")


def log_warning(msg: str):
    print(f"{YELLOW}[!] {msg}{RESET}")


def get_project_root() -> Path:
    return Path(__file__).parent.resolve()


def get_venv_python(venv_path: Path) -> Path:
    """Get the Python executable for the venv."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def get_venv_bin(venv_path: Path, name: str) -> Path:
    """Get the executable (uvicorn, streamlit) for the venv."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / f"{name}.exe"
    return venv_path / "bin" / name


class Launcher:
    def __init__(self):
        self.procs = []
        self.root = get_project_root()
        self.venv_path = self.root / "venv"

    def signal_handler(self, sig, frame):
        print()
        log_warning("Shutdown signal received. Stopping services...")
        self.stop()
        sys.exit(0)

    # ── Venv Management ────────────────────────────────────────────

    def venv_exists(self) -> bool:
        return self.venv_path.exists() and get_venv_python(self.venv_path).exists()

    def create_venv(self) -> bool:
        log_step(f"Creating virtual environment at {self.venv_path}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                log_error(f"Failed to create venv: {result.stderr}")
                return False
            log_success("Virtual environment created.")
            return True
        except Exception as e:
            log_error(f"Failed to create venv: {e}")
            return False

    def install_requirements(self) -> bool:
        log_step("Installing dependencies...")
        req_file = self.root / "requirements.txt"
        if not req_file.exists():
            log_error("requirements.txt not found!")
            return False

        pip_path = get_venv_bin(self.venv_path, "pip")
        result = subprocess.run(
            [str(pip_path), "install", "-r", str(req_file)],
            capture_output=False,
            text=True,
        )
        if result.returncode != 0:
            log_error("Failed to install dependencies.")
            return False

        log_success("Dependencies installed.")
        return True

    def ensure_venv(self) -> bool:
        """Ensure venv exists and has requirements installed."""
        if not self.venv_exists():
            if not self.create_venv():
                return False
            if not self.install_requirements():
                return False
        else:
            # Check if packages are installed by checking for uvicorn
            uvicorn_path = get_venv_bin(self.venv_path, "uvicorn")
            if not uvicorn_path.exists():
                log_step("Dependencies missing. Installing...")
                if not self.install_requirements():
                    return False
        return True

    # ── Service Starters ─────────────────────────────────────────────

    def start_backend(self) -> subprocess.Popen | None:
        uvicorn_bin = get_venv_bin(self.venv_path, "uvicorn")
        if not uvicorn_bin.exists():
            log_error("uvicorn not found. Reinstalling dependencies...")
            if not self.install_requirements():
                return None
            uvicorn_bin = get_venv_bin(self.venv_path, "uvicorn")

        backend_dir = self.root / "backend"
        log_step(f"Starting FastAPI backend...")

        proc = subprocess.Popen(
            [str(uvicorn_bin), "app:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return proc

    def start_frontend(self) -> subprocess.Popen | None:
        streamlit_bin = get_venv_bin(self.venv_path, "streamlit")
        if not streamlit_bin.exists():
            log_error("streamlit not found. Reinstalling dependencies...")
            if not self.install_requirements():
                return None
            streamlit_bin = get_venv_bin(self.venv_path, "streamlit")

        frontend_dir = self.root / "frontend"
        log_step(f"Starting Streamlit frontend...")

        proc = subprocess.Popen(
            [str(streamlit_bin), "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "127.0.0.1"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return proc

    # ── Output Streaming ─────────────────────────────────────────────

    def stream_output(self, label: str, proc: subprocess.Popen):
        try:
            for line in iter(proc.stdout.readline, ""):
                if line:
                    print(f"  {CYAN}[{label}]{RESET} {line.rstrip()}")
                if proc.poll() is not None:
                    break
        except Exception:
            pass

    def wait_for(self, url: str, retries: int = 30, delay: float = 0.5) -> bool:
        import urllib.request
        for _ in range(retries):
            try:
                urllib.request.urlopen(url, timeout=1)
                return True
            except Exception:
                time.sleep(delay)
        return False

    def wait_for_backend(self) -> bool:
        log_step("Waiting for backend to be ready...")
        if self.wait_for("http://127.0.0.1:8000/health"):
            log_success("Backend is ready!")
            return True
        log_error("Backend failed to start.")
        return False

    def wait_for_frontend(self) -> bool:
        log_step("Waiting for frontend to be ready...")
        if self.wait_for("http://127.0.0.1:8501"):
            log_success("Frontend is ready!")
            return True
        log_error("Frontend failed to start.")
        return False

    # ── Process Management ───────────────────────────────────────────

    def stop(self):
        log_warning("Stopping all services...")
        for proc in self.procs:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        self.procs.clear()
        log_success("All services stopped.")

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        log_header("AI Resume Analyzer Launcher")
        print(f"{BOLD}Project: {self.root}{RESET}\n")

        # Verify project structure
        if not (self.root / "backend").exists():
            log_error("backend/ directory not found!")
            sys.exit(1)
        if not (self.root / "frontend").exists():
            log_error("frontend/ directory not found!")
            sys.exit(1)
        if not (self.root / "requirements.txt").exists():
            log_error("requirements.txt not found!")
            sys.exit(1)

        # Setup venv + dependencies
        log_header("Setting Up Environment")
        if not self.ensure_venv():
            log_error("Failed to setup environment. Exiting.")
            sys.exit(1)

        # Start backend
        print()
        log_header("Starting Backend (FastAPI)")
        backend_proc = self.start_backend()
        if backend_proc is None:
            log_error("Failed to start backend.")
            sys.exit(1)
        self.procs.append(backend_proc)

        if not self.wait_for_backend():
            self.stop()
            sys.exit(1)

        # Start frontend
        print()
        log_header("Starting Frontend (Streamlit)")
        frontend_proc = self.start_frontend()
        if frontend_proc is None:
            log_error("Failed to start frontend.")
            self.stop()
            sys.exit(1)
        self.procs.append(frontend_proc)

        if not self.wait_for_frontend():
            self.stop()
            sys.exit(1)

        # All running
        print()
        log_header("All Services Running!")

        log(f"\n{GREEN}{BOLD}  Backend:   http://127.0.0.1:8000{RESET}")
        log(f"{GREEN}{BOLD}  Frontend:  http://127.0.0.1:8501{RESET}")
        log(f"\n  Press {BOLD}Ctrl+C{RESET} to stop all services\n")

        # Stream outputs concurrently
        import threading
        threads = [
            threading.Thread(target=self.stream_output, args=("BACKEND", backend_proc), daemon=True),
            threading.Thread(target=self.stream_output, args=("FRONTEND", frontend_proc), daemon=True),
        ]
        for t in threads:
            t.start()

        # Monitor for crashes
        try:
            while True:
                for i, proc in enumerate(self.procs):
                    if proc.poll() is not None:
                        name = "Backend" if i == 0 else "Frontend"
                        log_error(f"{name} process exited unexpectedly!")
                        self.stop()
                        sys.exit(1)
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()