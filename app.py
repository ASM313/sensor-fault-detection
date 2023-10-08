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
from flask import Flask,request,render_template

# app = FastAPI()
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# @app.get("/", tags=["authentication"])
# async def index():
#     return RedirectResponse(url="/docs")



@app.route("/train", methods=['GET', 'POST'])
def train_route():
    try:
        train_pipeline = TrainPipeline()
        if train_pipeline.is_pipeline_running:
            msg = "Training pipeline is already running."
            return render_template("index.html", msg=msg)
        train_pipeline.run_pipeline()
        msg = "Training successful !!"
        return render_template("index.html", msg=msg)
    except Exception as e:
        err_msg = f"Error Occurred! {e}"
        return render_template("error.html", msg=err_msg)

@app.get("/predict")
def predict_route():
    try:
        #get data from user csv file========================================

        df= []
        #convert csv file to dataframe=======================================

        #df=None
        model_resolver = ModelResolver(model_dir=SAVED_MODEL_DIR)
        if not model_resolver.is_model_exists():
            msg = "Model is not available"
            return render_template("index.html", msg=msg)
        
        best_model_path = model_resolver.get_best_model_path()
        model = load_object(file_path=best_model_path)
        y_pred = model.predict(df)
        df['predicted_column'] = y_pred
        df['predicted_column'].replace(TargetValueMapping().reverse_mapping(),inplace=True)
        
        #decide how to return file to user.
        """
        Write logic here
        """
        result = y_pred
        return render_template("index.html", result=result)
        
    except Exception as e:
        err_msg = f"Error Occurred! {e}"
        return render_template("error.html", msg=err_msg)
    

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000) 

# def main():
#     try:
#         training_pipeline = TrainPipeline()
#         training_pipeline.run_pipeline()
#     except Exception as e:
#         print(e)
#         logging.exception(e)


# if __name__=="__main__":
#     #main()
#     app_run(app, host=APP_HOST, port=APP_PORT)

  






# @app.route('/predict_data', methods=['GET', 'POST'])
# def predict_datapoint():
#     if request.method=="GET":
#         return render_template('index.html')
    
#     else:
#         data=CustomData(
#             cement=request.form.get('cement'),
#             blast_furnace_slag=request.form.get('blast_furnace_slag'),
#             fly_ash=request.form.get('fly_ash'),
#             water=request.form.get('water'),
#             superplasticizer=request.form.get('superplasticizer'),
#             coarse_aggregate=request.form.get('coarse_aggregate'),
#             fine_aggregate=float(request.form.get('fine_aggregate')),
#             age=float(request.form.get('age'))

#         )
#         pred_df=data.get_data_as_data_frame()
#         print(pred_df)
        
#         print("Before Prediction")

#         predict_pipeline=PredictPipeline()

#         print("Mid Prediction")

#         results=predict_pipeline.predict(pred_df)
        
#         print("After Prediction")
#         print("Predicted value is: ",results)
#         return render_template('index.html',results=results[0])
    