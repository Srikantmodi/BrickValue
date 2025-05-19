import os
import pickle
import numpy as np
import pandas as pd

# Global variables
__pipeline = None
DEFAULT_LOCATIONS = [
    "1st Block Jayanagar", "1st Phase JP Nagar", "2nd Phase JP Nagar", 
    "Electronic City", "Whitefield", "Sarjapur Road", "HSR Layout", 
    "Koramangala", "Bannerghatta Road", "MG Road", "Indiranagar"
]

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

def get_estimated_price(location, sqft, bhk, bath):
    """
    Predicts the price of a house based on the given features.
    """
    global __pipeline
    
    # Reload artifacts if needed
    if __pipeline is None:
        load_saved_artifacts()
    
    if __pipeline is None:
        print("Warning: Pipeline is still None after attempting to load")
        return "Pipeline not loaded"
    
    try:
        # Create input data as a DataFrame
        input_data = pd.DataFrame({
            'location': [location.lower().strip()],  # Convert location to lowercase
            'total_sqft': [sqft],
            'BHK': [bhk],
            'bath': [bath]
        })

        # Make prediction using the pipeline
        prediction = __pipeline.predict(input_data)[0]
        return round(prediction, 2)
    except Exception as e:
        print(f"Error predicting price: {e}")
        return None

def get_location_names():
    """
    Returns the list of available locations.
    """
    global __pipeline
    
    # Reload artifacts if needed
    if __pipeline is None:
        load_saved_artifacts()
    
    if __pipeline is None:
        print("Warning: Pipeline is still None after attempting to load")
        return DEFAULT_LOCATIONS
    
    try:
        # Extract unique locations from the OneHotEncoder in the pipeline
        encoder = __pipeline.named_steps['preprocessor'].named_transformers_['encoder']
        locations = encoder.categories_[0].tolist()
        return locations
    except Exception as e:
        print(f"Error extracting locations: {e}")
        return DEFAULT_LOCATIONS

def load_saved_artifacts():
    """
    Loads the saved pipeline from disk.
    """
    global __pipeline

    print("Loading saved artifacts...")
    artifacts_dir = os.path.join(current_dir, "artifacts")
    pipeline_file = os.path.join(artifacts_dir, "house_price_model_pipeline.pkl")
    
    try:
        with open(pipeline_file, "rb") as f:
            __pipeline = pickle.load(f)
        print("Loading saved artifacts...done")
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        print(f"Error loading pipeline: {e}")
        __pipeline = None

if __name__ == "__main__":
    load_saved_artifacts()
    print(get_location_names())
    if __pipeline:
        print(f"Example price prediction for {DEFAULT_LOCATIONS[0]}: "
              f"{get_estimated_price(DEFAULT_LOCATIONS[0], 1000, 3, 3)}")