import pandas as pd
import numpy as np
import time

N = 10000
data = {
    "date": pd.to_datetime(np.random.choice(pd.date_range('2020-01-01', '2023-12-31'), N)),
    "category": np.random.choice(["Lace", "Fingering", "Sport", "DK", "Worsted"], N),
    "yards": np.random.rand(N) * 1000,
    "meters": np.random.rand(N) * 900,
    "skeins": np.random.rand(N) * 5,
    "grams": np.random.rand(N) * 200,
}

df = pd.DataFrame(data)

start = time.time()
res1 = df["date"].dt.to_period("M").dt.to_timestamp("M")
print("dt.to_period:", time.time() - start)

# Try just to_numpy and pre-allocating dict, as the bottleneck in Model.get_animated_analytics_dataframe
# might just be creating the DataFrame from a list of dicts.
data_list = []
for i in range(10000):
    data_list.append({
        "date": pd.Timestamp('2020-01-01'),
        "category": "Fingering",
        "yards": 100.0,
        "meters": 90.0,
        "skeins": 1.0,
        "grams": 50.0,
    })

start = time.time()
df_from_list = pd.DataFrame(data_list)
print("pd.DataFrame(list):", time.time() - start)

start = time.time()
df_from_dict = pd.DataFrame({
    k: [d[k] for d in data_list] for k in data_list[0].keys()
})
print("pd.DataFrame(dict):", time.time() - start)
