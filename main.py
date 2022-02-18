
from fastapi import FastAPI, File, UploadFile
from tensorflow.keras.models import load_model
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import datetime
from google.cloud import storage

BASE_DIR = os.getcwd()
fraud_detection_model = load_model(f"{BASE_DIR}/model/fraud_detection_model_v1.h5")
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

app = FastAPI()
label = LabelEncoder()
def preprocess_(data):
    X_ = data.loc[:, [
                    'type',
                    'amount',
                    'oldbalanceOrg',
                    'newbalanceOrig',
                    'oldbalanceDest',
                    'newbalanceDest',
                    ]]
    
    
    X_.loc[:, ["type"]] = label.fit_transform(X_["type"])
    y_ = pd.DataFrame(data["isFraud"])
    return X_, y_

def label_encoder(x):
    if x == 1:
        return "Fraud"
    else:
        return "Non-Fraud"
@app.get("/")
def read_root():
    context = {}
    context["status"] = True
    context["message"] = "You've reach Team Tech Explorer's Public Test Endpoint." 
    return context

@app.post("/detect-fraud")
def detect_fraud(logs: UploadFile = File(...)):
    context = {}
    contentbyte = logs.file.read()
    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    filename = logs.filename
    blob = bucket.blob(filename)
    blob.upload_from_string(
        contentbyte,
        content_type=logs.content_type
    )
    context["uploaded_file_url"] = blob.public_url

    # filename = f"upload_{suffix_}.csv"
    # with open(f"./static/uploads/{filename}", 'wb') as f:
    #     f.write(contentbyte)
    # que_data = pd.read_csv(f"./static/uploads/{filename}")
    blob_open = bucket.get_blob(filename)
    your_file_contents = blob_open.download_as_string()

    # contents = gcs_file.read()
    que_data = pd.read_csv(your_file_contents)
    X_, _ = preprocess_(que_data)
    predicted_ = (fraud_detection_model.predict(X_)>0.5).astype("int32")
    X_["prediction"] = predicted_
    X_["prediction"] = X_["prediction"].apply(label_encoder)
    X_["type"] = label.inverse_transform(X_["type"])
    context = {}
    context["status"] = True
    context["data"] = X_.to_dict('records')
    # except Exception as e:
    #     context = {}
    #     context["status"] = False
    #     context["Error"] = e
    
    return context
