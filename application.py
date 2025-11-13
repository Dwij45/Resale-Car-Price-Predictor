from flask import Flask, render_template, request, redirect
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd
import numpy as np
import os
import logging

# logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
# cors = CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load model if present; ensure `model` is defined so predict() can check it safely
model = None
model_paths = [
    'LinearRegressionModel.pkl',
    'linear_regression_model.pkl',
    'model.pkl',
]
for mp in model_paths:
    if os.path.exists(mp):
        try:
            model = pickle.load(open(mp, 'rb'))
            logging.info(f"Loaded model from: {mp}")
            break
        except Exception as e:
            logging.exception(f"Found model file {mp} but failed to load: {e}")
            model = None

if model is None:
    logging.warning("No trained model file found in workspace. /predict will return an error until a model is provided.")

# Try to load car data (used to populate the form). If missing, the template will receive empty lists.
car = None
csv_candidates = [
    'Cleaned_Car_data.csv',
    'Cleaned_Car.csv',
    'Cleaned Car.csv',
    'CleanedCar.csv',
    'quikr_car.csv'
]
for csvf in csv_candidates:
    if os.path.exists(csvf):
        try:
            car = pd.read_csv(csvf)
            break
        except Exception:
            car = None
            continue

# # Try to load model file (provide clearer error if missing)
# model = None
# model_paths = [
#     'LinearRegressionModel.pkl',
#     'linear_regression_model.pkl',
#     'model.pkl',
# ]
# for mp in model_paths:
#     if os.path.exists(mp):
#         try:
#             model = pickle.load(open(mp, 'rb'))
#             logging.info(f"Loaded model from: {mp}")
#             break
#         except Exception as e:
#             logging.exception(f"Found model file {mp} but failed to load: {e}")
#             model = None

# if model is None:
#     logging.warning("No trained model file found in workspace. Prediction endpoint will fail until a model is provided.")

# # Try multiple possible CSV filenames so the app is less brittle to filename differences
# car = None
# csv_candidates = [
#     'Cleaned_Car_data.csv',
#     'Cleaned_Car.csv',
#     'Cleaned Car.csv',
#     'CleanedCar.csv'
# ]
# for csvf in csv_candidates:
#     if os.path.exists(csvf):
#         try:
#             car = pd.read_csv(csvf)
#             logging.info(f"Loaded car data from: {csvf}")
#             break
#         except Exception as e:
#             logging.exception(f"Found CSV {csvf} but failed to read: {e}")

# if car is None:
#     raise FileNotFoundError(f"Could not find any of the expected CSV files: {csv_candidates} in {os.getcwd()}")

@app.route('/')
def index():
    # Build values required by the template. If `car` wasn't loaded above, provide safe defaults.
    if car is not None:
        companies = sorted(car['company'].dropna().unique())
        years = sorted(car['year'].dropna().unique(), reverse=True)
        fuel_types = sorted(pd.unique(car['fuel_type'].dropna()))

        # Build a mapping: company -> list of models (strings)
        car_models_dict = {}
        for _, row in car.dropna(subset=['company', 'name']).iterrows():
            comp = row['company']
            name = row['name']
            car_models_dict.setdefault(comp, set()).add(name)

        # convert sets to sorted lists for JSON serializability
        for k in list(car_models_dict.keys()):
            car_models_dict[k] = sorted(list(car_models_dict[k]))

        # Insert a default placeholder option
        companies.insert(0, 'Select Company')
    else:
        companies = ['Select Company']
        years = []
        fuel_types = []
        car_models_dict = {}

    return render_template('index.html', companies=companies, car_models_dict=car_models_dict,
                           years=years, fuel_types=fuel_types)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    company=request.form.get('company')

    # NOTE: template uses name="car_model" for the model select (not 'car_models')
    car_model=request.form.get('car_model')
    year=request.form.get('year')
    fuel_type=request.form.get('fuel_type')
    driven=request.form.get('kilo_driven')

    # Validate model is available
    if model is None:
        logging.error('Prediction requested but no trained model is loaded.')
        return 'ERROR: model file not found on server. Please check server logs.'

    # Basic input validation
    missing = []
    if not car_model:
        missing.append('car_model')
    if not company:
        missing.append('company')
    if not year:
        missing.append('year')
    if not fuel_type:
        missing.append('fuel_type')
    if not driven:
        missing.append('kilo_driven')

    if missing:
        msg = f"ERROR: missing required fields: {', '.join(missing)}"
        logging.error(msg)
        return msg

    # Normalize numeric fields where appropriate
    try:
        year_val = int(year)
    except Exception:
        year_val = year

    try:
        kms_val = int(float(driven))
    except Exception:
        kms_val = driven

    try:
        df = pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                          data=np.array([car_model, company, year_val, kms_val, fuel_type]).reshape(1, 5))
        prediction = model.predict(df)
        logging.info(f"Prediction input: {df.to_dict(orient='records')}, output: {prediction}")
        return str(np.round(prediction[0], 2))
    except ValueError as ve:
        # Common issue: encoder sees unknown categories (e.g., None or a value not seen during training)
        logging.exception(f"Failed to predict (ValueError): {ve}")
        return 'ERROR: input contains values not seen by the trained model (pick valid company/model).' \
               ' Check that you selected a model and company present in the dataset.'
    except Exception as e:
        logging.exception(f"Failed to predict: {e}")
        return 'ERROR: failed to compute prediction. Check server logs.'



if __name__=='__main__':
    app.run(debug=True )