import datetime
import pandas as pd
import time

data_list = []
for i in range(10000):
    data_list.append({
        "date": "2020/01/01",
        "category": "Fingering",
        "yards": 100.0,
        "meters": 90.0,
        "skeins": 1.0,
        "grams": 50.0,
    })

start = time.time()
for d in data_list:
    try:
        d["date"] = datetime.datetime.strptime(d["date"], "%Y/%m/%d").date()
    except:
        pass
df = pd.DataFrame(data_list)
df["date"] = pd.to_datetime(df["date"])
print("datetime.strptime loop + pd.DataFrame + pd.to_datetime:", time.time() - start)
