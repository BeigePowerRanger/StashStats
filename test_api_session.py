from stashies.base_req import Req

class TestReq(Req):
    API_USERNAME: str = "test"
    API_KEY: str = "test"

req = TestReq()
# Assert session property exists and creates a requests.Session
s = req.session
print("Session class:", type(s))
print("Auth:", s.auth)
