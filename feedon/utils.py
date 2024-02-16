import requests
import logging

class AccessTokenInvalidError(Exception):
    pass

def validate_and_parse_request(resp: requests.Response):
    if resp.status_code == 401:
        raise AccessTokenInvalidError()

    try:
        return resp.json()
    except requests.exceptions.JSONDecodeError as error:
        logging.error(f'Could not parse JSON payload for timeline resp.remote_id')
        logging.error(f'Error: {error}')
        logging.error(f'Response payload:\n{resp.text}')
        raise error
