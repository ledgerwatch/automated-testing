import pytest
import requests

from tests.base_api_test_case import BaseApiTestCase


def get_block_info():
    t_c = BaseApiTestCase()
    session = requests.Session()
    latest_block_number = t_c.post(
        request_id=11,
        method="eth_blockNumber",
        params=[],
        session=session
    ).json()["result"]
    for i in range(10):
        block_info = t_c.post(
            request_id=11,
            method="eth_getBlockByNumber",
            params=[hex(int(latest_block_number, 16) - i - 1), True],
            session=session
        ).json()["result"]
        number = block_info["number"]
        try:
            to_address = block_info["transactions"][0]["to"]
            transaction_hash = block_info["transactions"][0]["hash"]
            return number, to_address, transaction_hash
        except IndexError:
            continue
    else:
        return "latest", None, None


class TestApiRequest(BaseApiTestCase):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.block_number, cls.to_address, cls.transaction_hash = get_block_info()

        cls.test_data = {
            "debug_traceBlockByNumber": [
                cls.block_number, {
                    "disableStack": True, "disableMemory": True,
                    "disableStorage": True,
                    "tracer": "callTracer",
                    "timeout": "300s"
                }
            ],
            "trace_filter": [
                {
                    "fromBlock": hex(int(cls.block_number, 16) - 5),
                    "toBlock": cls.block_number,
                    "toAddress": [
                        cls.to_address
                    ]
                }
            ],
            "eth_getTransactionReceipt": [
                cls.transaction_hash
            ]
        }

    @pytest.mark.api
    @pytest.mark.parametrize("method", ("debug_traceBlockByNumber", "trace_filter", "eth_getTransactionReceipt"))
    def test_api_response_validation(self, method):
        response = self.post(request_id=hex(77), method=method, params=self.test_data[method])
        assert response.status_code == 200, f"Got {response.status_code}, {response}"
        self.validate_schema(response=response, file_name=method)
