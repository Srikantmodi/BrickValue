import streamlit as st
import pickle
import numpy as np
import pandas as pd


model = pickle.load(open('random_forest_house_price_model.pkl', 'rb'))

dataset = pickle.load(open('dataset.pkl', 'rb'))


locations = dataset['location'].unique()

st.title("Bangalore House Price Prediction")

location = st.selectbox('Location', locations)
total_sqft = st.number_input('Total Square Foot', min_value=0.0, value=1000.0)
col1, col2 = st.columns(2)
with col1:
    bath = st.number_input('Number of Bathrooms', min_value=1, max_value=10, value=2)
with col2:
    bhk = st.number_input('Number of Bedrooms (BHK)', min_value=1, max_value=10, value=2)


if st.button('Predict'):
    input_data = pd.DataFrame([[location, total_sqft, bath, bhk]], columns=['location', 'total_sqft', 'bath', 'BHK'])
    prediction = model.predict(input_data)[0]
    st.write(f"The predicted price is {prediction:.2f} lakhs")

