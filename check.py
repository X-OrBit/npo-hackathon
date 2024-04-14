import pandas as pd

df = pd.read_csv("test.csv", encoding="utf-8")
df_count = df.groupby(by="client_id")["count_id"].count()

print(len(df))

print(df)
