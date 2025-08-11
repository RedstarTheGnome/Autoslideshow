import time
import pychromecast
import logging
from pychromecast.error import RequestFailed

# Set up logging for the script to see what's happening
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- CONFIGURATION ---

CHROMECAST_NAME = "Entryway TV"
URL_TO_CAST = "http://127.0.0.1:5000/"
WAIT_TIME_SECONDS = 10800 
# --- END CONFIGURATION ---

def restart_cast():
    """
    Finds the specified Chromecast, stops the current cast, and restarts it with the configured URL.
    """
    log.info(f"Looking for Chromecast named '{CHROMECAST_NAME}'...")
    
    # Discover all Chromecasts on the network with the specified name.
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[CHROMECAST_NAME])

    # Check if the Chromecast was found
    if not chromecasts:
        log.error(f"No Chromecast with name '{CHROMECAST_NAME}' found. Please check the name and your network connection.")
        return False
    
    # Select the first matching Chromecast
    cast = chromecasts[0]
    log.info(f"Found Chromecast: {cast.cast_info.friendly_name}. Waiting for it to be ready...")

    # Start the worker thread and wait for the device to be ready
    cast.wait()
    log.info("Chromecast is ready.")

    # Get the media controller
    mc = cast.media_controller
    try:
        log.info("Attempting to stop current media...")
        mc.stop()
        # Give the device a moment to process the stop command
        time.sleep(5)
    except RequestFailed:
        log.info("No media was playing, so the stop command failed gracefully.")
    
    # Start the new cast with the specified URL
    log.info(f"Starting new cast with URL: {URL_TO_CAST}")
    mc.play_media(URL_TO_CAST, "video/mp4")
    
    # Give the cast a moment to start
    mc.block_until_active(timeout=30)
    log.info("Cast successfully started.")
    
    # Clean up the browser discovery resources
    browser.stop_discovery()
    log.info("Restart complete. Waiting for the next scheduled restart.")
    
    return True

if __name__ == "__main__":
    while True:
        try:
            success = restart_cast()
            if success:
                log.info(f"Waiting for {WAIT_TIME_SECONDS / 3600} hours before the next restart...")
                time.sleep(WAIT_TIME_SECONDS)
            else:
                log.error("Restart failed. Retrying in 1 hour...")
                time.sleep(3600)
        except Exception as e:
            log.error(f"An unexpected error occurred: {e}. Retrying in 1 hour...", exc_info=True)
            time.sleep(3600)
