import os
import pandas as pd

os.environ["API_USERNAME"] = "test"
os.environ["API_KEY"] = "test"

from stashies.model import Model
from stashies.base_req import Req

m = Model(REQ=Req())
# Mock data
stash_list = [
    {
        "created_at": "2023/01/01 12:00:00",
        "updated_at": "2023/02/01 12:00:00",
        "yarn": {"yarn_weight_name": "Fingering", "yardage": 100, "grams": 50},
        "packs": [{"total_yards": 100, "total_meters": 90, "skeins": 1, "total_grams": 50, "project_id": 1}],
        "history": [{"date": "2023-01-15", "yards": -10, "meters": -9, "skeins": -0.1, "grams": -5}]
    }
]
proj_map = {1: pd.Timestamp("2023-01-10")}

try:
    df1 = m.get_animated_analytics_dataframe(stash_list, proj_map)
    print("df1 shape:", df1.shape)
    print("df1 dates:", df1["date"].unique())
    df2 = m.get_analytics_dataframe(stash_list, proj_map)
    print("df2 shape:", df2.shape)
    print("df2 dates:", df2["date"].unique())
    print("Successfully verified pandas changes!")
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
