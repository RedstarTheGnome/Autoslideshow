import time
import subprocess
import logging
import os

# Set up logging for the script to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- CONFIGURATION ---
# The full path to the catt.exe executable.
# IMPORTANT: This path must be correct for your system.
CATT_PATH = r"C:\Users\JordanRedpath\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\catt.exe"

# The URL of your locally hosted webpage.
URL_TO_CAST = "http://10.66.0.38:5000/"

# The time to wait between refreshes, in seconds.
# 3 hours = 3 * 60 * 60 = 10800 seconds.
WAIT_TIME_SECONDS = 10800 

# The name of your Chromecast device.
CHROMECAST_DEVICE_NAME = "Entryway TV"
# --- END CONFIGURATION ---

def run_catt_command():
    """
    Constructs and runs the catt command using subprocess.
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
    
    try:
        log.info(f"Running command: {command}")
        # Use subprocess.run to execute the command.
        # `capture_output=True` will grab the command's output.
        # `text=True` formats the output as a string.
        result = subprocess.run(command, env=env, capture_output=True, text=True, check=True)
        log.info("Catt command executed successfully.")
        log.info(f"Command output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to run catt command. Error code: {e.returncode}")
        log.error(f"Error output:\n{e.stderr}")
    except FileNotFoundError:
        log.error(f"Catt executable not found at: {CATT_PATH}. Please check the path.")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    while True:
        try:
            run_catt_command()
            log.info(f"Cast complete. Waiting for {WAIT_TIME_SECONDS / 3600} hours before next refresh...")
            time.sleep(WAIT_TIME_SECONDS)
        except KeyboardInterrupt:
            log.info("Script terminated by user.")
            break
        except Exception as e:
            log.error(f"An error occurred in the main loop: {e}. Retrying in 1 hour...", exc_info=True)
            time.sleep(3600)
