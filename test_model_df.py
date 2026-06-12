import pandas as pd
import numpy as np

# Simulate a large amount of data for the dataframe
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

# Test the old operations and measure speed or memory
# Specifically:
# df["date"] = df["date"].dt.to_period("M").dt.to_timestamp("M")
import time

start = time.time()
df["date_m1"] = df["date"].dt.to_period("M").dt.to_timestamp("M")
print("dt.to_period:", time.time() - start)

start = time.time()
df["date_m2"] = df["date"].dt.floor('ME') if hasattr(df["date"].dt, 'floor') else df["date"].dt.to_period("M").dt.to_timestamp("M")
print("dt.floor/etc:", time.time() - start)

start = time.time()
# The old groupby: df.groupby(["date", "category"])[["yards", "meters", "skeins", "grams"]].sum().reset_index()
df.groupby(["date_m1", "category"])[["yards", "meters", "skeins", "grams"]].sum().reset_index()
print("groupby:", time.time() - start)
