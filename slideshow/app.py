from flask import Flask, jsonify, send_from_directory, render_template
import os

app = Flask(__name__)


IMAGE_FOLDER = r'G:\Shared drives\Screen\static\images' #ammend to picture folder
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
    app.run(debug=True, port=5000)