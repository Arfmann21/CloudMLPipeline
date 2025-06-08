import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import joblib
import tempfile
from google.cloud import storage
import xgboost as xgb


def main(request):
    df = pd.read_csv("gs://progetto_clean_dataset_bucket/dataset.csv")

    X = df.drop("class", axis=1)
    y = df["class"]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        objective='multi:softprob',  # o 'binary:logistic' se hai solo 2 classi
        eval_metric='mlogloss',  # o 'logloss' per binario
        random_state=42
    )
    model.fit(X_train, y_train)

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        joblib.dump(model, tmp.name)
        local_path = tmp.name

    bucket_name = "progetto_clean_dataset_bucket"
    destination_blob = "model.pkl"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(local_path)

    return "OK", 200
