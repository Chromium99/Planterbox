from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import os
from PIL import Image
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for Android app

# Create images directory if it doesn't exist
IMAGES_DIR = "received_images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
    print(f"Created directory: {IMAGES_DIR}")

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Get image data from request
        image_data = request.data
        
        if not image_data:
            return jsonify({'error': 'No image data received'}), 400
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Save image for viewing in checkBackend.py
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath, "JPEG")
        print(f"Image saved: {filepath}")
        
        # Get image properties
        width, height = image.size
        format_type = image.format
        
        # Process the image (you can add your image processing logic here)
        # For example, you could run ML model inference, image analysis, etc.
        
        # Prepare JSON response
        response_data = {
            'status': 'success',
            'message': 'Image received successfully',
            'image_info': {
                'width': width,
                'height': height,
                'format': format_type,
                'size_bytes': len(image_data)
            },
            'analysis': {
                'processed': True,
                'timestamp': str(datetime.now())
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend server is running'}), 200

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so Android device can connect
    # Change port if needed
    print("Starting Flask server on http://0.0.0.0:5000")
    print("Make sure to update SERVER_URL in frontend.java with your computer's IP address")
    # Exclude checkBackend.py from auto-reloader to prevent restart loops
    app.run(host='0.0.0.0', port=5000, debug=True, extra_files=[])