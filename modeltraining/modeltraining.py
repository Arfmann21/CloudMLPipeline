import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import joblib
import tempfile
from google.cloud import storage

def main(request):
    df = pd.read_csv("gs://progetto_clean_dataset_bucket/dataset.csv")

    X = df.drop("class", axis=1)
    y = df["class"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modello SVC
    model = SVC(kernel='linear')  # puoi provare anche 'rbf', 'poly'
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
