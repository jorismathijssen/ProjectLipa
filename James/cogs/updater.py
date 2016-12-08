import subprocess
import sys
import os

def update():
    """ Updates James by pulling the latests commits from 
    github and restarting itself"""
    subprocess.call("./cogs/update.sh")
    restart_program()

def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

