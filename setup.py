#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   This file is part of PyBuilder
#
#   Copyright 2011-2020 PyBuilder Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import subprocess
import sys
import glob
import shutil
import platform
from pathlib import Path
from sys import version_info

py3 = version_info[0] == 3
py2 = not py3
if py2:
    FileNotFoundError = OSError


def check_python_version():
    """Check if Python 3.11 is installed."""
    print("Checking Python version...")
    try:
        result = subprocess.run(["python3.11", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Python 3.11 found.")
            return "python3.11"
        else:
            print("Python 3.11 not found.")
            return None
    except FileNotFoundError:
        print("Python 3.11 not found.")
        return None


def install_python():
    """Install Python 3.11 based on the OS."""
    print("Installing Python 3.11...")
    os_type = platform.system()
    if os_type == "Linux":
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "-y", "python3.11", "python3.11-venv"])
    elif os_type == "Darwin":  # macOS
        subprocess.run(["brew", "update"])
        subprocess.run(["brew", "install", "python@3.11"])
    elif os_type == "Windows":
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
        subprocess.run([python_path, "-m", "venv", ".venv"])

    print("Activating virtual environment...")
    os_type = platform.system()
    if os_type == "Windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
    else:
        activate_script = venv_dir / "bin" / "activate"

    if not activate_script.exists():
        print("Failed to create virtual environment.")
        sys.exit(1)

    # Activate the virtual environment
    if os_type == "Windows":
        os.system(str(activate_script))
    else:
        os.environ["VIRTUAL_ENV"] = str(venv_dir)
        os.environ["PATH"] = f"{venv_dir}/bin:" + os.environ["PATH"]
        print(f"Virtual environment activated: {venv_dir}")


def install_requirements():
    """Install dependencies from requirements.txt."""
    print("Installing dependencies...")
    subprocess.run(["pip", "install", "--upgrade", "pip"])
    if not Path("requirements.txt").exists():
        print("requirements.txt not found.")
        sys.exit(1)
    subprocess.run(["pip", "install", "-r", "requirements.txt"])


def install_from_git():
    """Install the project from a Git repository."""
    print("Installing project from Git repository...")
    git_url = "https://github.com/sayakghorai34/Human-Detection-and-Counting.git"  # Replace with your GitHub repository
    branch = "main"  # Replace with the branch you want to install from
    subprocess.run(["pip", "install", f"git+{git_url}@{branch}"])


def setup_environment():
    """Ensure Python 3.11, virtual environment, and requirements are set up."""
    python_path = check_python_version()
    if not python_path:
        install_python()
        python_path = "python3.11"

    create_and_activate_venv(python_path)
    install_requirements()
    install_from_git()  # Install from Git repository


def install_pyb():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pybuilder"])
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


script_dir = os.path.dirname(os.path.realpath(__file__))
exit_code = 0

try:
    setup_environment()  # Set up Python environment

    subprocess.check_call(["pyb", "--version"])
except FileNotFoundError as e:
    if py3 or py2 and e.errno == 2:
        install_pyb()
    else:
        raise
except subprocess.CalledProcessError as e:
    if e.returncode == 127:
        install_pyb()
    else:
        sys.exit(e.returncode)

try:
    from pybuilder.cli import main
    # verbose, debug, skip all optional...
    if main("-v", "-X", "-o", "--reset-plugins", "clean", "package"):
        raise RuntimeError("PyBuilder build failed")

    from pybuilder.reactor import Reactor
    reactor = Reactor.current_instance()
    project = reactor.project
    dist_dir = project.expand_path("$dir_dist")

    for src_file in glob.glob(os.path.join(dist_dir, "*")):
        file_name = os.path.basename(src_file)
        target_file_name = os.path.join(script_dir, file_name)
        if os.path.exists(target_file_name):
            if os.path.isdir(target_file_name):
                shutil.rmtree(target_file_name)
            else:
                os.remove(target_file_name)
        shutil.move(src_file, script_dir)
    setup_args = sys.argv[1:]
    subprocess.check_call([sys.executable, "setup.py"] + setup_args, cwd=script_dir)
except subprocess.CalledProcessError as e:
    exit_code = e.returncode
sys.exit(exit_code)