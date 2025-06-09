import streamlit as st
from google.cloud import storage
import requests
import url_secret as us
import pandas as pd
import ast
import io

st.set_page_config(layout = "wide")

def load_to_bucket(dataset):

    with st.spinner("Preprocessing in corso..."):
        storage_client = storage.Client()
        bucket_name = "progetto_dataset_bucket"
        destination_blob_name = "car.data"

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_file(dataset)

    start_training()

def start_training():
    with st.spinner("Addestramento in corso..."):
        requests.post(us.get_training())

def inference(inf_with_file, file, buying, maint, doors, persons, lug_boot, safety):

    if inf_with_file:
        return requests.post(f"{us.get_inference()}?inf_with_file=True", files={"file": file})

    buying = 0 if buying == "low" else (1 if buying == "med" else (2 if buying == "high" else 3))
    maint = 0 if maint == "low" else (1 if maint == "med" else (2 if maint == "high" else 3))
    doors = 2 if doors == "2" else (3 if doors == "3" else (4 if doors == "4" else 5))
    persons = 2 if persons == "2" else (4 if persons == "4" else 5)
    lug_boot = 0 if lug_boot == "small" else (1 if lug_boot == "med" else 2)
    safety = 0 if safety == "low" else (1 if safety == "med" else 2)

    return requests.post(f"{us.get_inference()}?inf_with_file=False&buying={buying}&maint={maint}&doors={doors}&persons={persons}&lug_boot={lug_boot}&safety={safety}")


def main():

    if "dataset_loaded" not in st.session_state:
        st.session_state["dataset_loaded"] = False
        st.header("Benvenuto, inizia caricando il dataset")

    if not st.session_state["dataset_loaded"]:
        dataset = st.file_uploader(label = "Seleziona file", type = "data")

        if dataset is not None:
            st.session_state["dataset_loaded"] = True
            load_to_bucket(dataset)
            st.subheader("Modello pronto per l'inferenza")
            st.rerun()

    else:
        result = None
        st.header("Inserisci i dati per classificare il record")

        form_inference, or_text, file_inference = st.columns([1, 0.2, 2])

        with form_inference:
            with st.form("inference_form"):
                buying = st.selectbox("Buying", options = ["low", "med", "high", "v-high"])
                maint = st.selectbox("Maint", options = ["low", "med", "high", "v-high"])
                doors = st.selectbox("Doors", options = ["2", "3", "4", "5-more"])
                persons = st.selectbox("Persons", options = ["2", "4", "more"])
                lug_boot = st.selectbox("Lug Boot", options = ["small", "med", "big"])
                safety = st.selectbox("Safety", options = ["low", "med", "high"])

                submitted  = st.form_submit_button("Classifica")

                if submitted:
                    result = inference(False, None, buying, maint, doors, persons, lug_boot, safety)

                    if result is not None:
                        result = result.content.decode().strip()
                        result = "acc" if result == "0" else (
                            "good" if result == "1" else ("unacc" if result == "2" else "vgood"))
                        st.subheader("Etichetta: " + result)

        with file_inference:
            dataset_inference_uploader = st.file_uploader(label = "Seleziona file per l'inferenza", type = "csv")

            if dataset_inference_uploader is not None:
                df = pd.read_csv(io.BytesIO(dataset_inference_uploader.getvalue()))
                result = inference(True, dataset_inference_uploader, 0, 0, 0, 0, 0, 0)

                if result is not None:
                    df["class"] = ast.literal_eval(result.content.decode())

                    st.dataframe(df)



main()