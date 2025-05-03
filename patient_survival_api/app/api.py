import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
print(parent)
print(root)
sys.path.append(str(root))

import json
from typing import Any 

from fastapi import APIRouter, HTTPException, Body
from fastapi.encoders import jsonable_encoder
import joblib
import os
import numpy as np
# import __version__ as _version

from app import __version__, schemas
from app.config import settings

api_router = APIRouter()

model_path = Path(root) / "model" / "model.joblib"
print(f"Loading model from {model_path}")
print(os.listdir(Path(root) / "model"))
model = joblib.load(model_path)


@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    health = schemas.Health(
        name=settings.PROJECT_NAME , 
        api_version=__version__ , 
        # model_version=model_version
    )

    return health.dict()


example_input = {
    "inputs": [
        {
            "age": 75,
            "anaemia": 0,
            "creatinine_phosphokinase": 582,
            "diabetes": 0,
            "ejection_fraction": 20,
            "high_blood_pressure": 1,
            "platelets": 265000,
            "serum_creatinine": 1.9,
            "serum_sodium": 130,
            "sex": 1,
            "smoking": 0,
            "time": 4,
            "DEATH_EVENT": 1
        }
    ]
}

@api_router.post("/predict", response_model=schemas.PredictionResults, status_code=200)
async def predict(input_data: schemas.MultipleDataInputs = Body(..., example=example_input)) -> Any:
    """
    Predict patient survival based on health metrics.
    """
    try:
        # Extract the first input
        print(input_data.inputs[0])
        input_instance = input_data.inputs[0]
        # Prepare feature array
        features = np.array([[ 
            input_instance.age,
            input_instance.anaemia,
            input_instance.creatinine_phosphokinase,
            input_instance.diabetes,
            input_instance.ejection_fraction,
            input_instance.high_blood_pressure,
            input_instance.platelets,
            input_instance.serum_creatinine,
            input_instance.serum_sodium,
            input_instance.sex,
            input_instance.smoking,
            input_instance.time
        ]])
        print(features)
        # Make prediction with your model (assuming 'model' is loaded)
        prediction = model.predict(features)
        print(prediction)
        # Map prediction to label (e.g., dead or alive)
        prediction_label = "Death" if int(prediction[0]) == 1 else "Survived"
        print(prediction_label)
        result = {
            "errors": None,
            "version": __version__,
            "predictions": int(prediction[0]),
            "prediction_event": prediction_label
        }
    except Exception as e:
        result = {
            "errors": str(e),
            "version": __version__,
            "predictions": None,
            "prediction_event": ""
        }

    return result