import time
import pychromecast
import logging
from pychromecast.error import RequestFailed

# Set up logging for the script to see what's happening
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Replace 'Your Chromecast Name' with the exact name of your Chromecast.
# You can find this name in the Google Home app.
CHROMECAST_NAME = "Entryway TV"

# Replace 'http://your-url-here.com' with the full URL of the media you want to cast.
# Make sure this is a URL that the Chromecast's default media receiver can play.
URL_TO_CAST = "http://your-url-here.com"

# The time to wait between restarts, in seconds.
# 3 hours = 3 * 60 * 60 = 10800 seconds.
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

    # We use a try-except block to handle the case where no media is currently playing.
    # This prevents the script from crashing if it tries to stop a non-existent session.
    try:
        log.info("Attempting to stop current media...")
        mc.stop()
        # Give the device a moment to process the stop command
        time.sleep(5)
    except RequestFailed:
        log.info("No media was playing, so the stop command failed gracefully.")
    
    # Start the new cast with the specified URL
    log.info(f"Starting new cast with URL: {URL_TO_CAST}")
    # For a web page or image, you can often use a generic content_type like 'video/mp4' as a placeholder.
    # The Chromecast's default receiver is usually smart enough to figure it out.
    mc.play_media(URL_TO_CAST, "video/mp4")
    
    # Give the cast a moment to start
    mc.block_until_active(timeout=30)
    log.info("Cast successfully started.")
    
    # Clean up the browser discovery resources
    # This has been updated to use the non-deprecated method.
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
