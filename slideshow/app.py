# app.py
import sys
import os
import io
# 1. FIX: Added render_template to the import
from flask import Flask, jsonify, send_from_directory, send_file, render_template
# Import Pillow for image processing
from PIL import Image
# Import pillow_heif and register the HEIF opener
from pillow_heif import register_heif_opener

# Register the HEIF opener so Pillow can read HEIC files
register_heif_opener()

# Global variables to store the command-line arguments (timing)
TIME_MS = '3000'
REFRESH_MS = '5000'

# Get the image folder path from command-line arguments
# sys.argv[1] is the image folder path passed from the Tkinter GUI.
if len(sys.argv) > 1:
    IMAGE_FOLDER = sys.argv[1]
else:
    # Use a default path if no parameter is provided (for standalone testing)
    IMAGE_FOLDER = 'static/images' 

app = Flask(__name__)

# Updated to include '.heic' and '.heif'
ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.heic', '.heif'}

@app.route('/')
def index():
    # Now correctly using the imported render_template function
    # You might want to pass the timings here for the front-end to use:
    # return render_template('index.html', time_ms=TIME_MS, refresh_ms=REFRESH_MS)
    return render_template('index.html')

# 2. FEATURE: Add a route to expose the timings to the client-side JavaScript
@app.route('/config')
def get_config():
    return jsonify({
        'slideshow_time_ms': TIME_MS,
        'refresh_time_ms': REFRESH_MS
    })

@app.route('/images')
def get_images():
    try:
        files = os.listdir(IMAGE_FOLDER)
    except FileNotFoundError:
        print(f"Error: Image folder not found at {IMAGE_FOLDER}")
        return jsonify([])
    except Exception as e:
        print(f"Error listing files in {IMAGE_FOLDER}: {e}")
        return jsonify([])

    # Create a list of image URLs, filtering by allowed extensions
    images = [f'/images/{f}' for f in files
              if os.path.splitext(f)[1].lower() in ALLOWED_EXTS]
    images.sort()
    return jsonify(images)

@app.route('/images/<path:filename>')
def image(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)
    
    # Check if the file is HEIC/HEIF
    if filename.lower().endswith(('.heic', '.heif')):
        try:
            # 1. Open the HEIC file using Pillow 
            img = Image.open(file_path)
            
            # 2. Save the image data to an in-memory buffer as JPEG
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=90)
            img_io.seek(0)
            
            # 3. Serve the JPEG data with the correct MIME type
            # NOTE: You might need to add a cache control header if the HEIC files change often
            return send_file(img_io, mimetype='image/jpeg')

        except Exception as e:
            # Log the error and serve the raw file as a fallback
            print(f"Error converting HEIC file {filename}: {e}")
            return send_from_directory(IMAGE_FOLDER, filename) 
    
    # Serve all other files (PNG, JPG, GIF, etc.) normally
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    # Retrieve and set the global time and refresh time parameters
    # The Tkinter GUI passes time and refresh time as sys.argv[2] and sys.argv[3]
    if len(sys.argv) > 2:
        TIME_MS = sys.argv[2] 
    if len(sys.argv) > 3:
        REFRESH_MS = sys.argv[3]
    
    print(f"Serving images from: {IMAGE_FOLDER}")
    print(f"Slideshow timing: {TIME_MS}ms, Refresh timing: {REFRESH_MS}ms")
    
    # Run the Flask app
    app.run(debug=True, port=5000)