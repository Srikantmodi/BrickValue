from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pickle
import pandas as pd
import os
import logging
import json

# Configure Flask app
app = Flask(__name__, static_url_path='')
# Apply CORS with explicit configuration
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type"], "methods": ["GET", "POST"]}})

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
__pipeline = None
__locations = None

# Load the saved artifacts
def load_saved_artifacts():
    global __pipeline
    global __locations
    
    logging.info("Loading saved artifacts...")
    try:
        # Define artifact paths
        artifacts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
        logging.info(f"Artifacts directory: {artifacts_dir}")
        
        # Check which model file exists
        pipeline_file = os.path.join(artifacts_dir, "house_price_model_pipeline.pkl")
        alternative_file = os.path.join(artifacts_dir, "banglore_home_prices_model.pickle")
        
        if os.path.exists(pipeline_file):
            logging.info(f"Found model file: {pipeline_file}")
            with open(pipeline_file, "rb") as f:
                __pipeline = pickle.load(f)
        elif os.path.exists(alternative_file):
            logging.info(f"Found alternative model file: {alternative_file}")
            with open(alternative_file, "rb") as f:
                __pipeline = pickle.load(f)
        else:
            logging.error("No model file found!")
            
        # Load columns from JSON
        columns_file = os.path.join(artifacts_dir, "columns.json")
        if os.path.exists(columns_file):
            logging.info(f"Found columns file: {columns_file}")
            with open(columns_file, 'r') as f:
                data_columns = json.load(f)['data_columns']
                __locations = data_columns[3:]  # First 3 are sqft, bath, bhk
                logging.info(f"Loaded {len(__locations)} locations")
        else:
            logging.error("No columns.json file found!")
            
    except Exception as e:
        logging.error(f"Error loading artifacts: {e}")
        return False
    
    return True

@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'index.html' is in the 'templates' folder

@app.route('/<path:path>')
def serve_static_files(path):
    logging.info(f"Serving static file: {path}")
    return send_from_directory('.', path)

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    """
    Endpoint to get the list of available locations.
    """
    logging.info("get_location_names endpoint called")
    response = jsonify({
        'locations': __locations if __locations else [],
        'status': 'success'
    })
    # Explicitly set CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    logging.info(f"Returning {len(__locations) if __locations else 0} locations")
    return response

@app.route('/predict_home_price', methods=['POST', 'OPTIONS'])
def predict_home_price():
    """
    Endpoint to predict the price of a house based on input features.
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    logging.info("predict_home_price endpoint called")
    try:
        # Parse request data
        if not request.is_json:
            logging.error("Request data is not in JSON format")
            return jsonify({'error': 'Invalid input format. Expected JSON.', 'status': 'failure'}), 400

        data = request.get_json()
        logging.info(f"Received data: {data}")

        # Extract parameters
        total_sqft = float(data.get('total_sqft', 0))
        bhk = int(data.get('bhk', 0))
        bath = int(data.get('bath', 0))
        location = data.get('location', '').lower().strip()

        logging.info(f"Processing: sqft={total_sqft}, location={location}, bhk={bhk}, bath={bath}")

        # Ensure the pipeline is loaded
        if __pipeline is None:
            load_saved_artifacts()
            if __pipeline is None:
                return jsonify({'error': 'Could not load model.', 'status': 'failure'}), 500

        # Prepare input data as a DataFrame
        input_data = pd.DataFrame({
            'location': [location],
            'total_sqft': [total_sqft],
            'BHK': [bhk],
            'bath': [bath]
        })

        # Make prediction using the pipeline
        prediction = __pipeline.predict(input_data)[0]
        estimated_price = round(prediction, 2)
        logging.info(f"Estimated price: {estimated_price}")

        # Return result with explicit CORS headers
        response = jsonify({'estimated_price': estimated_price, 'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logging.error(f"Error in predict_home_price: {e}")
        response = jsonify({'error': str(e), 'status': 'failure'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == "__main__":
    logging.info("Starting Python Flask Server For Home Price Prediction...")
    # Load artifacts at server startup
    load_saved_artifacts()
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)