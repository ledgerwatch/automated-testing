import json
import logging

import jsonschema
import requests

from api import schema_path
from tests.conftest import option


class BaseApiTestCase:

    @classmethod
    def setup_class(cls):
        cls.session = requests.Session()
        cls.session.headers.update({"Content-Type": "application/json"})

    def post(self, request_id, method, params=None, session=None):
        if session:
            self.session = session
            self.session.headers.update({"Content-Type": "application/json"})
        data = {
            "id": request_id,
            "method": method,
            "params": params,
            "jsonrpc": "2.0"
        }
        data = json.dumps(data, sort_keys=True)
        logging.info(f"Sending POST request with data:\n{data}\n")
        response = self.session.post(url=option.url, data=data)
        logging.info(f"Got response:\n {response.content}")
        return response

    def validate_schema(self, response, file_name):
        path = f"{schema_path}/{file_name}.json"
        with open(path, "r", encoding='utf-8') as schema:
            # try:
            response = response.json()
            # except AttributeError:
            #     pass
            jsonschema.validate(instance=response, schema=json.load(schema))
