from google.cloud import storage
import joblib
import io
import numpy as np

def main(request):
    bucket_name = "progetto_clean_dataset_bucket"
    blob_name = "model.pkl"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    model_bytes = blob.download_as_bytes()

    model = joblib.load(io.BytesIO(model_bytes))

    buying = int(request.args.get("buying"))
    maint = int(request.args.get("maint"))
    doors = int(request.args.get("doors"))
    persons = int(request.args.get("persons"))
    lug_boot = int(request.args.get("lug_boot"))
    safety = int(request.args.get("safety"))

    input_data = np.array([[buying, maint, doors, persons, lug_boot, safety]])

    print(input_data)
    y_pred = model.predict(input_data)

    return y_pred.tolist(), 200