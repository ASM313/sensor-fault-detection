from sensor.configuration.mongo_db_connection import MongoDBClient
from sensor.exception import SensorException
import os,sys
from sensor.logger import logging
from sensor.pipeline import training_pipeline
from sensor.pipeline.training_pipeline import TrainPipeline
import os
from sensor.utils.main_utils import read_yaml_file
from sensor.constant.training_pipeline import SAVED_MODEL_DIR
from fastapi import FastAPI
from sensor.constant.application import APP_HOST, APP_PORT
from starlette.responses import RedirectResponse
from uvicorn import run as app_run
from fastapi.responses import Response
from sensor.ml.model.estimator import ModelResolver,TargetValueMapping
from sensor.utils.main_utils import load_object
from fastapi.middleware.cors import CORSMiddleware
import os
from flask import Flask,request,render_template, redirect
import pandas as pd
import numpy as np


app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/train", methods=['GET', 'POST'])
def train_route():
    logging.info("User request for Training..")
    train_pipeline = TrainPipeline()
    if train_pipeline.is_pipeline_running:
        msg = "Training pipeline is already running."
        return render_template("index.html", msg=msg)
    train_pipeline.run_pipeline()
    logging.info("Training successful..!!")
    msg = "Training successful !!"
    return render_template("result.html",msg=msg)
    
@app.route("/predict", methods=['GET', 'POST'])
def predict_route():
    try:
        logging.info("User request for Prediction..")    

        #get data from user csv file
        csv_file = request.files['csvFile']
        logging.info("User uploaded csv file.")

        if csv_file.filename == '':
            return 'No selected file'

        if csv_file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
            csv_file.save(file_path)
            logging.info('File uploaded successfully')

        #convert csv file to dataframe
        user_input_csv_df = pd.read_csv(file_path)
        logging.info("CSV to Dataframe")
        print(user_input_csv_df)
        
        # Convert dataframe to numpy array
        user_input_csv_array = np.array(user_input_csv_df)
        logging.info("Dataframe to np array ")
        
        print("User input : ", user_input_csv_array)
        
        model_resolver = ModelResolver(model_dir=SAVED_MODEL_DIR)
        if not model_resolver.is_model_exists():
            msg = "Model is not available"
            return render_template("index.html", msg=msg)
        
        best_model_path = model_resolver.get_best_model_path()
        logging.info("Best model chosen..")

        model = load_object(file_path=best_model_path)
        logging.info("Model loaded...")

        y_pred = model.predict(user_input_csv_array)
        print("Predicted class is :", y_pred[0])
        logging.info("Predicted class showed:")
        
        logging.info("Appending predicted column with dataframe.")
        user_input_csv_df['predicted_class'] = y_pred
        user_input_csv_df['predicted_class'].replace(TargetValueMapping().reverse_mapping(),inplace=True)
        
        #decide how to return file to user.
        """
        Write logic here
        """

        if  y_pred[0]==1:
            result = "Positive"

        else:
            result = "Negative"    
        logging.info("Showing result to User at Front end")

        return render_template("index.html", result=result)
        
    except Exception as e:
        err_msg = f"Error Occurred! {e}"
        return render_template("error.html", msg=err_msg)
    

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 