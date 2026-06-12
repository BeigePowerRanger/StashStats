from stashies.base_req import Req
import requests
from requests.auth import HTTPBasicAuth

class FastReq(Req):
    @property
    def session(self):
        if not hasattr(self, '_session'):
            object.__setattr__(self, '_session', requests.Session())
            self._session.auth = HTTPBasicAuth(self.API_USERNAME, self.API_KEY)
        return self._session

req = FastReq(API_USERNAME="test", API_KEY="test")
print(req.session)
print(req.session.auth)
