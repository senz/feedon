import requests

class AccessTokenInvalidError(Exception):
    pass

def validate_request(resp: requests.Response):
    if resp.status_code == 401:
        raise AccessTokenInvalidError()

