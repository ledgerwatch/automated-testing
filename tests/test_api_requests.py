import pytest
import requests

from tests.base_api_test_case import BaseApiTestCase


class TestApiRequest(BaseApiTestCase):
    block_info = BaseApiTestCase().post(
        request_id=11,
        method="eth_getBlockByNumber",
        params=["latest", True],
        session=requests.Session()
    ).json()["result"]
    block_number = block_info["number"]
    to_address = block_info["transactions"][0]["to"]
    transaction_hash = block_info["transactions"][0]["hash"]

    test_data = [
        ("debug_traceBlockByNumber", [block_number,
                                      {
                                          "disableStack": True, "disableMemory": True, "disableStorage": True,
                                          "tracer": "callTracer",
                                          "timeout": "300s"
                                      }
                                      ]
         ),
        ("trace_filter", [
            {
                "fromBlock": hex(int(block_number, 16) - 5),
                "toBlock": block_number,
                "toAddress": [
                    to_address
                ]
            }
        ]
         ),
        ("eth_getTransactionReceipt", [
            transaction_hash
        ]
         )
    ]

    @pytest.mark.api
    @pytest.mark.parametrize("method, params", test_data)
    def test_api_response_validation(self, method, params):
        response = self.post(request_id=hex(77), method=method, params=params)
        assert response.status_code == 200, f"Got {response.status_code}, {response}"
        self.validate_schema(response=response, file_name=method)
