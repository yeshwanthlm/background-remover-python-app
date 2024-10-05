from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from rembg import remove
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For secure session cookies

# Configure logging
logging.basicConfig(level=logging.INFO)

# Limit file size (max 10 MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Allowed file extensions for images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select a file
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file format. Only PNG, JPG, and JPEG are allowed.', 'danger')
            return redirect(request.url)
        
        try:
            # Open the uploaded image
            input_image = Image.open(file.stream)
        except UnidentifiedImageError:
            flash('Invalid image file. Please upload a valid image.', 'danger')
            return redirect(request.url)
        
        try:
            # Remove background from the image
            output_image = remove(input_image, post_process_mask=True)
            img_io = BytesIO()
            output_image.save(img_io, 'PNG')
            img_io.seek(0)

            # Return the processed image
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='image_rmbg.png')
        
        except Exception as e:
            logging.error(f"Error during background removal: {e}")
            flash('Failed to remove background from the image. The background might not be suitable for removal.', 'danger')
            return redirect(request.url)
    
    return render_template('index.html')

if __name__ == '__main__':
    # Use this for local development. For production, use gunicorn or a similar WSGI server.
    app.run(host='0.0.0.0', debug=False, port=5100)
