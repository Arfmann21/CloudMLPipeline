import pandas as pd

def main():
    # Crea un DataFrame a partire dal file txt contenente il dataset
    df = pd.read_csv("gs://progetto_dataset_bucket/car.data", sep=",", header=None)
    df.columns = ["buying", "maint", "doors", "persons", "lug_boot", "safety", "class"]

    # TRASFORMAZIONI APPLICATE:
    # 0. Rimozione dei record con valori nulli
    # 1. Codifica delle feature categoriche in valori numerici
    # 2. Rimozione dei record con valori nulli

    df.dropna()

    # 3. Codifica delle feature categoriche in valori numerici
    for i in range(0, len(df.index)):
        # Gli attributi categorici di scala (low, med, etc. e small, med, etc.) vengono codificati da 0 a salire
        df.loc[i, "buying"] = 0 if df["buying"][i] == "low" else (
            1 if df["buying"][i] == "med" else (2 if df["buying"][i] == "high" else 3))
        df.loc[i, "maint"] = 0 if df["maint"][i] == "low" else (
            1 if df["maint"][i] == "med" else (2 if df["maint"][i] == "high" else 3))
        df.loc[i, "lug_boot"] = 0 if df["lug_boot"][i] == "small" else (1 if df["lug_boot"][i] == "med" else 2)
        df.loc[i, "safety"] = 0 if df["safety"][i] == "low" else (1 if df["safety"][i] == "med" else 2)

        # Per doors e persons, le stringhe che rappresentano interi vengono trasformati nei corrispettivi interi, il valore limite (come 5-more) nell'intero che vi è contenuto
        df.loc[i, "doors"] = 1 if df["doors"][i] == "1" else (
            2 if df["doors"][i] == "2" else (3 if df["doors"][i] == "3" else (4 if df["doors"][i] == "4" else 5)))
        df.loc[i, "persons"] = 2 if df["persons"][i] == "2" else (4 if df["persons"][i] == "4" else 5)

    df.to_csv("gs://progetto_clean_dataset_bucket/dataset.csv", index=False)