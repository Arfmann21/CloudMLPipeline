from google.cloud import storage
import joblib
import io
import numpy as np
import pandas as pd

def main(request):
    bucket_name = "progetto_clean_dataset_bucket"
    blob_name = "model.pkl"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    model_bytes = blob.download_as_bytes()

    model = joblib.load(io.BytesIO(model_bytes))

    inf_with_file = bool(request.args.get("inf_with_file"))

    if inf_with_file:
        df = pd.read_csv(request.files["file"])

        return model.predict(df).tolist(), 200

    buying = int(request.args.get("buying"))
    maint = int(request.args.get("maint"))
    doors = int(request.args.get("doors"))
    persons = int(request.args.get("persons"))
    lug_boot = int(request.args.get("lug_boot"))
    safety = int(request.args.get("safety"))

    input_data = np.array([[buying, maint, doors, persons, lug_boot, safety]])

    y_pred = model.predict(input_data)

    return str(y_pred.item(0)), 200