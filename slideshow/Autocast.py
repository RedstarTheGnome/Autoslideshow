import time
import subprocess
import logging
import os
import sys
import threading
import socket
from datetime import datetime

# Set up logging for the script to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- CONFIGURATION ---
# The full path to the catt.exe executable.
# IMPORTANT: This path must be correct for your system.
CATT_PATH = r"C:\Users\JordanRedpath\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\catt.exe"

# Dynamically get the local IPv4 address and set the URL
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # Connect to an external host to find the local IP
    local_ip = s.getsockname()[0]
    s.close()
    URL_TO_CAST = f"http://{local_ip}:5000/"
except Exception as e:
    log.error(f"Could not determine local IP address: {e}")
    # Fallback to a common local IP if an error occurs
    URL_TO_CAST = "http://127.0.0.1:5000/"

# The time to wait between refreshes, in seconds.
WAIT_TIME_SECONDS = 120

# The name of your Chromecast device.
CHROMECAST_DEVICE_NAME = "Entryway TV"
# --- END CONFIGURATION ---

def run_catt_command(retries=3, delay=10):
    """
    Constructs and runs the catt command with retry logic.
    Retries up to `retries` times with a `delay` between each attempt.
    """
    log.info("Starting the cast refresh process...")
    
    # We construct the command as a list of strings. This is the safest way to
    # run external commands with subprocess, especially with paths that have spaces.
    command = [
        CATT_PATH,
        "cast_site",
        URL_TO_CAST
    ]

    # Set the CATT_DEVICE environment variable for this specific command.
    env = os.environ.copy()
    env["CATT_DEVICE"] = CHROMECAST_DEVICE_NAME
    
    for attempt in range(retries):
        try:
            log.info(f"Attempt {attempt + 1}/{retries}: Running command: {command}")
            # Use subprocess.run to execute the command.
            # `capture_output=True` will grab the command's output.
            # `text=True` formats the output as a string.
            result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
            result.check_returncode() # Raise an exception if the command failed
            log.info("Catt command executed successfully.")
            log.info(f"Command output:\n{result.stdout}")
            return # Exit the function on success
        except subprocess.TimeoutExpired:
            log.warning(f"Attempt {attempt + 1}/{retries} timed out. Retrying...")
            time.sleep(delay)
        except subprocess.CalledProcessError as e:
            log.error(f"Attempt {attempt + 1}/{retries} failed. Error code: {e.returncode}")
            log.error(f"Error output:\n{e.stderr}")
            time.sleep(delay)
        except FileNotFoundError:
            log.error(f"Catt executable not found at: {CATT_PATH}. Please check the path.")
            # This is a critical error, so we don't retry.
            return
        except Exception as e:
            log.error(f"An unexpected error occurred on attempt {attempt + 1}/{retries}: {e}", exc_info=True)
            time.sleep(delay)

    log.error("All retry attempts failed. Will wait for the next cycle.")

if __name__ == "__main__":
    while True:
        try:
            log.info("--- Starting new cycle at %s ---", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            run_catt_command()
            log.info(f"Cast complete. Waiting for {WAIT_TIME_SECONDS} seconds before the next refresh...")
            time.sleep(WAIT_TIME_SECONDS)
        except KeyboardInterrupt:
            log.info("Script terminated by user.")
            break
        except Exception as e:
            log.error(f"An error occurred in the main loop: {e}. Retrying after a short delay...", exc_info=True)
            time.sleep(60) # Wait for 1 minute before the next cycle