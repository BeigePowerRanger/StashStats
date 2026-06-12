import pandas as pd
import time

# Create list of 10000 dicts
data_list = []
for i in range(10000):
    data_list.append({
        "date": "2020-01-01",
        "category": "Fingering",
        "yards": 100.0,
        "meters": 90.0,
        "skeins": 1.0,
        "grams": 50.0,
    })

start = time.time()
df = pd.DataFrame(data_list)
df["date"] = pd.to_datetime(df["date"])
print("pd.DataFrame(list) + pd.to_datetime:", time.time() - start)

start = time.time()
for d in data_list:
    d["date"] = pd.to_datetime(d["date"])
df = pd.DataFrame(data_list)
print("pd.to_datetime loop + pd.DataFrame(list):", time.time() - start)
