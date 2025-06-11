import streamlit as st
from google.cloud import storage
import requests
import url_secret as us
import pandas as pd
import ast
import io
from google.cloud import pubsub_v1

st.set_page_config(layout = "wide")

preprocessing_completed = False

def sub_callback(message):
    message.ack()
    global preprocessing_completed
    preprocessing_completed = True
    st.write(preprocessing_completed)

def load_to_bucket(dataset):

    # Show a loading for uploading the dataset into the bucket
    with st.spinner("Preprocessing in corso..."):
        storage_client = storage.Client()
        bucket_name = "progetto_dataset_bucket"
        destination_blob_name = "car.data"

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_file(dataset)

        # The frontend must know when the preprocessing is completed before doing anything
        # This is achieved using Google Cloud Pub/Sub pattern
        p_id = us.get_id()
        s_id = us.get_sub_id()
        global preprocessing_completed

        subscriber = pubsub_v1.SubscriberClient()
        subsctibtion_path = subscriber.subscription_path(p_id, s_id)
        subscriber.subscribe(subsctibtion_path, callback = sub_callback)

        # Do nothing until the preprocessing is completed
        while not preprocessing_completed:
            st.spinner()

    # Once the preprocessing is done, start training the machine learning model
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

    return requests.post(f"{us.get_inference()}?buying={buying}&maint={maint}&doors={doors}&persons={persons}&lug_boot={lug_boot}&safety={safety}")


def form_inference_handler():
    with st.form("inference_form"):
        buying = st.selectbox("Buying", options=["low", "med", "high", "v-high"])
        maint = st.selectbox("Maint", options=["low", "med", "high", "v-high"])
        doors = st.selectbox("Doors", options=["2", "3", "4", "5-more"])
        persons = st.selectbox("Persons", options=["2", "4", "more"])
        lug_boot = st.selectbox("Lug Boot", options=["small", "med", "big"])
        safety = st.selectbox("Safety", options=["low", "med", "high"])

        submitted = st.form_submit_button("Classifica")

        if submitted:
            result = inference(False, None, buying, maint, doors, persons, lug_boot, safety)

            if result is not None:
                result = result.content.decode().strip()
                result = "acc" if result == "0" else (
                    "good" if result == "1" else ("unacc" if result == "2" else "vgood"))
                st.subheader("Etichetta: " + result)


def file_inference_handler():

    dataset_inference_uploader = st.file_uploader(label="Seleziona file per l'inferenza", type="csv")

    if dataset_inference_uploader is not None:
        df = pd.read_csv(io.BytesIO(dataset_inference_uploader.getvalue()))
        result = inference(True, dataset_inference_uploader, 0, 0, 0, 0, 0, 0)

        result_classes = ast.literal_eval(result.content.decode())
        result_classes_str = []

        with st.spinner():

            if result is not None:
                for i in range(0, len(result_classes)):
                    result_classes_str.append("acc" if result_classes[i] == 0 else (
                        "good" if result_classes[i] == 1 else ("unacc" if result_classes[i] == 2 else "vgood")))

                df["class"] = result_classes_str

                st.dataframe(df)

def main():

    # Use session state to dinamically change the UI to show inference when the dataset is uploaded
    if "dataset_loaded" not in st.session_state:
        st.session_state["dataset_loaded"] = False
        st.session_state["file_inf"] = False
        st.header("Benvenuto, inizia caricando il dataset")

    if not st.session_state["dataset_loaded"]:
        dataset = st.file_uploader(label = "Seleziona file", type = "data")

        if dataset is not None:
            st.session_state["dataset_loaded"] = True
            load_to_bucket(dataset)
            st.rerun()

    else:
        st.header("Inserisci i dati per classificare il record")

        # Create three columns: the first one to display the form, the third to display the file uploader and the dataframe
        # and the middle to add some space in between
        form_inference, or_text, file_inference = st.columns([1, 0.2, 2])

        with form_inference:
            form_inference_handler()

        with file_inference:
            file_inference_handler()

main()