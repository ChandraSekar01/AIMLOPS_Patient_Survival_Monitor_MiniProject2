import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))


from typing import Any

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api import api_router
from app.config import settings

curr_path = str(Path(__file__).parent)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

root_router = APIRouter()

import os
import joblib
model_path = Path(root) / "model" / "model.joblib"
print(f"Loading model from {model_path}")
print(os.listdir(Path(root) / "model"))
model = joblib.load(model_path)


###########################
# Prometheus code
import pandas as pd
import prometheus_client as prom
from sklearn.metrics import accuracy_score, f1_score
from app import schemas
# import os
# print(os.getcwd())
# print(os.listdir("/app"))

test_data = pd.read_csv("/app/heart_failure_clinical_records_dataset.csv")
print(test_data.shape)
f1_metric = prom.Gauge('patient_survival_f1_score', 'F1 score for XGBoost')
# def make_prediction(input_df: pd.DataFrame) -> dict:  # schemas.MultipleDataInputs = Body(..., example=example_input)
def make_prediction(input_df: schemas.MultipleDataInputs) -> Any:
    predictions = []
    print("Shape")
    print(input_df)
    print(input_df.shape)


    if input_df.empty:
        print("Warning: input_df is empty!")
        return {'predictions': []}

    for index, row in input_df.iterrows():
        try:
            input_instance = schemas.DataInputSchema(**row.to_dict())
            # input_instance = **row.to_dict()
            # input_instance = schemas.MultipleDataInputs(inputs=[schemas.DataInputSchema(**row.to_dict())])
            print(input_instance)
            features = [[
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
            ]]
            print("features")
            print(features)
            pred = model.predict(features)
            print("Pred")
            print(pred)
            predictions.append(int(pred[0]))
        except Exception as e:
            print(f"Error in prediction: {e}")
            predictions.append(None)

    return {'predictions': predictions}

# Function to update metrics
def update_metrics():
    # Sample 100 data points for evaluation
    sample_df = test_data.sample(100, random_state=42)
    test_features = sample_df.drop('DEATH_EVENT', axis=1)
    test_labels = sample_df['DEATH_EVENT'].values

    results = make_prediction(test_features)

    # Filter out invalid predictions
    valid_predictions = [
        pred for pred in results['predictions'] if pred is not None
    ]
    print("valid pred")
    print(valid_predictions)
    valid_labels = [
        label for pred, label in zip(results['predictions'], test_labels) if pred is not None
    ]
    print("valid_labels")
    print(valid_labels)

    # Calculate F1 score
    if valid_predictions:
        f1 = f1_score(valid_labels, valid_predictions)  #.round(3)
        # print(f1)
        f1_metric.set(f1)

@app.get("/metrics")
async def get_metrics():
    update_metrics()
    print(prom.generate_latest())
    return Response(media_type="text/plain",content=prom.generate_latest())

###########################


@root_router.get("/")
def index(request: Request) -> Any:
    """Basic HTML response."""
    body = (
        "<html>"
        "<body style='padding: 10px;'>"
        "<h1>Welcome to the API</h1>"
        "<div>"
        "Check the docs: <a href='/docs'>here</a>"
        "</div>"
        "</body>"
        "</html>"
    )

    return HTMLResponse(content=body)


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 