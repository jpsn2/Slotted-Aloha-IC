import os
import sys
import subprocess
import pandas as pd
from tqdm.auto import tqdm
from main import main
from datetime import datetime

dataframes = []

# Quantidade de experimentos
experiments = 30

start = datetime.now()
# Realizando experimentos
for i in tqdm(range(experiments)):
    main(time_sleep=False)
    os.rename("data/metrics.csv", f"data/metrics_{i}.csv")

end = datetime.now()
print(f"""
      DURATION: {end - start}
      """)
# Carregando dataframes
for i in tqdm(range(experiments)):
    try:
        df = pd.read_csv(f"data/metrics_{i}.csv")
        df["experiment"] = i
        dataframes.append(df)
    except:
        print("Nenhum experimento foi excutado")
        sys.exit(0)

# Calculando média
df = pd.concat(dataframes)
print(df.groupby("network").agg({"THROUGHPUT": "mean"}))
print("___"*10)
print(df.groupby("network").agg({"SUCCESS": "mean"}))
print("___"*10)
print(df.groupby("network").agg({"IDLE": "mean"}))
print("___"*10)
print(df.groupby("network").agg({"BUSY": "mean"}))
print("___"*10)
print(df.groupby("network").agg({"COLLISION": "mean"}))
print("___"*10)
print(df.groupby("network").agg({"CONFIGURATION_NETWORK": "mean"}))
print("___"*10)
print("Total de pacotes: ", df["GENERATING_PACKAGES"].sum())
print("\nFIM DA SIMULAÇÃO")