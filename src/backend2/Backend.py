import base64
from datetime import datetime
import os

from flask import Flask, request, jsonify

from shareimg import get_image_info

app = Flask(__name__)

# Directory to save received images
UPLOAD_FOLDER = 'received_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Check if image data is present
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400
        image_file = request.files['image']

        # Read the uploaded bytes once so we can both inspect and save them
        image_bytes = image_file.read()
        if not image_bytes:
            return jsonify({
                'status': 'error',
                'message': 'Empty image payload'
            }), 400

        # Extract simple metadata from the image bytes
        image_info = get_image_info(image_bytes)

        # Save the image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'image_{timestamp}.jpg'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Get image size
        file_size = len(image_bytes)
        
        # Create JSON response with image information
        response_data = {
            'status': 'success',
            'message': 'Image processed successfully',
            'data': {
                'filename': filename,
                'size_bytes': file_size,
                'width': image_info['width'],
                'height': image_info['height'],
                'total_pixels': image_info['total_pixels'],
                'received_at': datetime.now().isoformat(),
                'saved_path': filepath
            }
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'server': 'Python Image Server'}), 200

if __name__ == '__main__':
    print("Starting Python Image Processing Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
