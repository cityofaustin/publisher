def authenticate(auth):
    if not isinstance(auth, dict):
        return false
    method = auth.get("method")
    if method == "token":
        return auth.get("token") == "TEST_TOKEN"
    elif method == "github":
        # TODO
        return false
    return false
