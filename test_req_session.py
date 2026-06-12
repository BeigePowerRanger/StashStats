from stashies.base_req import Req

class TestReq(Req):
    API_USERNAME: str = "test"
    API_KEY: str = "test"

req = TestReq()
print(hasattr(req, 'session'))
print(req.session)
