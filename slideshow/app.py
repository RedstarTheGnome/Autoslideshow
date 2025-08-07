# app.py
import sys
from flask import Flask, jsonify, send_from_directory, render_template
import os

# Get the image folder path from command-line arguments
# The first argument (sys.argv[0]) is the script name itself.
# sys.argv[1] would be the first parameter passed.
if len(sys.argv) > 1:
    IMAGE_FOLDER = sys.argv[1]
else:
    # Use a default path if no parameter is provided
    IMAGE_FOLDER = r'G:\Shared drives\Screen\static\images'

app = Flask(__name__)
ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.WebP'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images')
def get_images():
    files = os.listdir(IMAGE_FOLDER)
    images = [f'/images/{f}' for f in files
              if os.path.splitext(f)[1].lower() in ALLOWED_EXTS]
    images.sort()
    return jsonify(images)

@app.route('/images/<path:filename>')
def image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    print(f"Serving images from: {IMAGE_FOLDER}")
    app.run(debug=True, port=5000)