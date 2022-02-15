from audioop import tostereo
from typing import Optional
from fastapi import FastAPI

import os
# import cloudstorage
# from google.appengine.api import app_identity

app = FastAPI()

# BUCKET_NAME = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

@app.get("/")
def read_root():
    context = {}
    context["BUCKET_NAME"] = BUCKET_NAME
    return context

