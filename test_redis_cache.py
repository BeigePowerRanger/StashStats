import os
import fakeredis
from stashies.model import Model
from stashies.base_req import Req
from stashies.db import DBManager

os.environ["API_USERNAME"] = "test"
os.environ["API_KEY"] = "test"
os.environ["RAVELRY_USERNAME"] = "testuser"

DBManager.get_pool()
m = Model(REQ=Req())

# Inject fakeredis
class FakeRedisModel(Model):
    def get_redis(self):
        if self._redis is None:
            self._redis = fakeredis.FakeStrictRedis(decode_responses=True)
        return self._redis

m = FakeRedisModel(REQ=Req())

class MockReq(Req):
    def get_request(self, endpoint, params=None):
        if "list.json" in endpoint:
            return {"unified_stash": [{"stash": {"id": 1, "updated_at": "2023-01-01"}}]}
        return {"stash": {"id": 1, "updated_at": "2023-01-01", "packs": []}}

m.REQ = MockReq()

stashes = m.get_stash_list()
if stashes is not None:
    print(f"Successfully retrieved {len(stashes)} stash items.")
else:
    print("No stashes retrieved or error occurred.")
