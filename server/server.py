from flask import Flask, request, jsonify
from flask_cors import CORS
import util

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/classify_image', methods=['POST'])
def classify_image():
    image_data = request.form['image_data'] # Base64 image
    result = util.classify_image(image_data)
    return jsonify(result)

if __name__ == "__main__":
    print("Starting Python Flask Server For Avengers Classifier")
    util.load_saved_artifacts() #Loads saved model to the memory
    app.run(port=5000)