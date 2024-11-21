import os
import subprocess
import sys
from pathlib import Path
from setuptools import setup

setup(
    name="human-detection-and-counting",
    version="0.1.0",
    install_requires=[
        "pybuilder>=0.13.4",
    ],
)


def check_python_version():
    """Check if Python 3.11 is installed."""
    print("Checking Python version...")
    commands = [["python3.11", "--version"], ["python3", "--version"], ["python", "--version"] ]

    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and "3.11" in result.stdout:
                print(f"Python 3.11 found with command: {' '.join(cmd)}")
                return cmd[0]  # Return the executable name
        except FileNotFoundError:
            continue  # Try the next command

    print("Python 3.11 not found.")
    return None


def install_python():
    """Install Python 3.11 based on the OS."""
    print("Installing Python 3.11...")
    os_type = os.name
    if os_type == "posix":
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3.11", "python3.11-venv"])
    elif os_type == "nt":
        print("Please install Python 3.11 manually from https://www.python.org/downloads/")
        sys.exit(1)
    else:
        print(f"Unsupported OS: {os_type}")
        sys.exit(1)


def create_and_activate_venv(python_path):
    """Create and activate a virtual environment."""
    print("Creating a virtual environment...")
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        subprocess.run([python_path, "-m", "venv", str(venv_dir)])

    pip_path = venv_dir / "bin" / "pip" if os.name != "nt" else venv_dir / "Scripts" / "pip.exe"
    if not pip_path.exists():
        print("pip is missing in the virtual environment. Installing pip...")
        subprocess.run([python_path, "-m", "ensurepip"])
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"])


def install_requirements():
    """Install dependencies."""
    print("Installing dependencies...")
    pip_path = Path(".venv") / ("bin" / "pip" if os.name != "nt" else "Scripts/pip.exe")
    if pip_path.exists():
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"])
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])


def setup_environment():
    """Set up the environment."""
    python_path = check_python_version()
    if not python_path:
        install_python()
        python_path = "python3.11"

    create_and_activate_venv(python_path)
    install_requirements()


def install_pyb():
    """Install PyBuilder."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pybuilder"])
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    try:
        setup_environment()
        subprocess.check_call(["pyb", "--version"])
    except FileNotFoundError as e:
        install_pyb()
    except subprocess.CalledProcessError as e:
        if e.returncode == 127:
            install_pyb()
        else:
            sys.exit(e.returncode)
