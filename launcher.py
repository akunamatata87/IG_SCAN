"""
Launcher for InstaAnalytics Pro - Streamlit App
This script launches the Streamlit application and opens it in the default browser.
"""
import subprocess
import sys
import os
import webbrowser
import time
import socket
import shutil


def find_free_port():
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def find_python():
    """Find the actual Python interpreter on the system."""
    # 1. Try 'python' on PATH
    python_path = shutil.which("python")
    if python_path and "WindowsApps" not in python_path:
        return python_path

    # 2. Try 'python3' on PATH
    python_path = shutil.which("python3")
    if python_path and "WindowsApps" not in python_path:
        return python_path

    # 3. Try common install locations
    common_paths = [
        os.path.expanduser(r"~\AppData\Local\Python\bin\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python314\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python313\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Python\Python310\python.exe"),
        r"C:\Python314\python.exe",
        r"C:\Python313\python.exe",
        r"C:\Python312\python.exe",
    ]
    for p in common_paths:
        if os.path.isfile(p):
            return p

    # 4. Try py launcher
    py_path = shutil.which("py")
    if py_path:
        return py_path

    return None


def main():
    # Get the directory where this executable/script is located
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        python_exe = find_python()
        if not python_exe:
            print("ERROR: Could not find Python on this system.")
            print("Please make sure Python is installed.")
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        python_exe = sys.executable

    script_path = os.path.join(app_dir, "IG_Scan-V2.0.py")

    if not os.path.exists(script_path):
        print(f"ERROR: Could not find {script_path}")
        print("Make sure IG_Scan-V2.0.py is in the same folder as this executable.")
        input("Press Enter to exit...")
        sys.exit(1)

    port = find_free_port()
    url = f"http://localhost:{port}"

    print("=" * 50)
    print("  📸 InstaAnalytics Pro - Launcher")
    print("=" * 50)
    print(f"\n  Python: {python_exe}")
    print(f"  Server: {url}")
    print("  The app will open in your browser shortly...")
    print("\n  Press Ctrl+C in this window to stop the server.")
    print("=" * 50)

    # Open browser after a short delay
    import threading
    def open_browser():
        time.sleep(3)
        webbrowser.open(url)
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch Streamlit using the REAL Python interpreter
    try:
        subprocess.run([
            python_exe, "-m", "streamlit", "run",
            script_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"\nERROR: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
