from flask import Flask, request, jsonify, render_template, send_from_directory
import util
from flask_cors import CORS
import os

# Configure Flask app
app = Flask(__name__)
# Enable CORS for all domains and routes, with support for credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def home():
    return send_from_directory('.', 'app.html')

@app.route('/app.js')
def serve_js():
    return send_from_directory('.', 'app.js')

@app.route('/app.css')
def serve_css():
    return send_from_directory('.', 'app.css')

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    try:
        # Ensure artifacts are loaded
        util.load_saved_artifacts()
        locations = util.get_location_names()
        print(f"Returning {len(locations)} locations")
        response = jsonify({
            'locations': locations
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error in get_location_names: {e}")
        import traceback
        traceback.print_exc()
        # Return default locations on error
        response = jsonify({
            'error': str(e),
            'locations': ['1st Block Jayanagar', '1st Phase JP Nagar', 'Electronic City', 'Whitefield', 'Sarjapur Road']
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

@app.route('/predict_home_price', methods=['POST', 'OPTIONS'])
def predict_home_price():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        print("Received prediction request")
        print("Form data:", request.form)
        print("Files:", request.files)
        print("Content-Type:", request.headers.get('Content-Type'))
        
        # Extract data from form or JSON
        total_sqft = None
        location = None
        bhk = None
        bath = None
        
        # Try to get data from form first
        if request.form:
            try:
                total_sqft = float(request.form.get('total_sqft', 0))
                location = request.form.get('location', '')
                bhk = int(request.form.get('bhk', 0))
                bath = int(request.form.get('bath', 0))
            except (ValueError, TypeError) as e:
                print(f"Error parsing form data: {e}")
        
        # If not in form, try JSON
        if total_sqft is None and request.is_json:
            data = request.get_json()
            try:
                total_sqft = float(data.get('total_sqft', 0))
                location = data.get('location', '')
                bhk = int(data.get('bhk', 0))
                bath = int(data.get('bath', 0))
            except (ValueError, TypeError) as e:
                print(f"Error parsing JSON data: {e}")
        
        # Check if we got the data
        if total_sqft is None or location is None or bhk is None or bath is None:
            return jsonify({'error': 'Missing input parameters', 'estimated_price': 'Error'}), 400
            
        print(f"Processing: sqft={total_sqft}, location={location}, bhk={bhk}, bath={bath}")

        # Validate inputs
        if total_sqft <= 0 or not location or bhk <= 0 or bath <= 0:
            return jsonify({'error': 'Invalid input parameters', 'estimated_price': 'Error'}), 400

        # Make prediction
        util.load_saved_artifacts()  # Ensure artifacts are loaded
        estimated_price = util.get_estimated_price(location, total_sqft, bhk, bath)
        print(f"Estimated price: {estimated_price}")

        # Return the result
        response = jsonify({
            'estimated_price': estimated_price
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        print(f"Error in predict_home_price: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'error': str(e), 'estimated_price': 'Error'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    # Load artifacts at server startup
    try:
        util.load_saved_artifacts()
        print("Artifacts loaded successfully")
    except Exception as e:
        print(f"Error loading artifacts: {e}")
        print("Server will start but predictions may not work correctly")
    
    # Run the app - use port 5000 explicitly
    app.run(host='0.0.0.0', port=5000, debug=True)