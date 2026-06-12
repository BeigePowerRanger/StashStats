# Look at why the tests failed:
# The E2E tests are patching `requests.get` / `requests.post` etc.
# But because we switched to `self.session.get()`, the patch on `requests.get` is completely ignored!
# We need to change `tests/test_e2e.py` to patch `requests.Session.get` and `requests.Session.post`
# or we can revert the E2E tests to patch `Req.get_request` / `Req.post_request` directly.
# Let's inspect test_e2e.py.
