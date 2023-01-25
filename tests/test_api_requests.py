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
        block_number = block_info["number"]
        block_hash = block_info["hash"]
        try:
            to_address = block_info["transactions"][0]["to"]
            transaction_hash = block_info["transactions"][0]["hash"]
            return block_number, block_hash, to_address, transaction_hash
        except IndexError:
            continue
    else:
        return "latest", None, None, None


def get_filter():
    try:
        return BaseApiTestCase().post(
            request_id=11,
            method="eth_newPendingTransactionFilter",
            params=[],
            session=requests.Session()
        ).json()["result"]
    except KeyError:
        return None


class TestApiRequest(BaseApiTestCase):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.block_number, cls.block_hash, cls.to_address, cls.transaction_hash = get_block_info()
        cls.filter = get_filter()

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
            ],
            "eth_getTransactionByHash": [
                cls.transaction_hash
            ],
            "trace_block": [cls.block_number],
            "erigon_blockNumber": ["latest"],
            "erigon_forks": [],
            "eth_blockNumber": [],
            "eth_chainId": [],
            "eth_protocolVersion": [],
            "eth_syncing": [],
            "eth_gasPrice": [],
            "eth_maxPriorityFeePerGas": [],
            "eth_feeHistory": ["0x5", "latest", []],
            "eth_getBlockByHash": [cls.block_hash, True],
            "eth_getBlockByNumber": [cls.block_number, True],
            "eth_getBlockTransactionCountByHash": [cls.block_hash],
            "eth_getBlockTransactionCountByNumber": [cls.block_number],
            "eth_getTransactionByBlockHashAndIndex": [cls.block_hash, "0x0"],
            "eth_getTransactionByBlockNumberAndIndex": [cls.block_number, "0x0"],
            "eth_getBlockReceipts": ["latest"],
            "eth_call": [
                {
                    "from": '0x67b1d87101671b127f5f8714789C7192f7ad340e',
                    "to": '0xa94f5374Fce5edBC8E2a8697C15331677e6EbF0B'
                },
                cls.block_number
            ],
            "eth_estimateGas": [
                {
                    "from": '0x67b1d87101671b127f5f8714789C7192f7ad340e',
                    "to": '0xa94f5374Fce5edBC8E2a8697C15331677e6EbF0B'
                }
            ],
            "eth_getBalance": ['0x67b1d87101671b127f5f8714789C7192f7ad340e', 'latest'],
            "eth_getTransactionCount": ['0x67b1d87101671b127f5f8714789C7192f7ad340e', 'latest'],
            "eth_getStorageAt": ['0x67b1d87101671b127f5f8714789C7192f7ad340e', '0x0', 'latest'],
            "eth_newFilter": [{"fromBlock": cls.block_number}],
            "eth_newBlockFilter": [],
            "eth_newPendingTransactionFilter": [],
            "eth_uninstallFilter": [cls.filter],
            "eth_getLogs": [{"fromBlock": cls.block_number}],
            "eth_accounts": [],
            "eth_signTypedData": [],
            "eth_coinbase": []

        }

    @pytest.mark.api
    @pytest.mark.parametrize(
        "method", (
                "trace_filter",
                "eth_getTransactionReceipt",
                "trace_block",
                "erigon_blockNumber",
                "erigon_forks",
                "eth_getTransactionByHash",
                "eth_blockNumber",
                "eth_chainId",
                "eth_protocolVersion",
                "eth_syncing",
                "eth_gasPrice",
                "eth_maxPriorityFeePerGas",
                "eth_feeHistory",
                "eth_getBlockByHash",
                "eth_getBlockByNumber",
                "eth_getBlockTransactionCountByHash",
                "eth_getBlockTransactionCountByNumber",
                "eth_call",
                "eth_estimateGas",
                "eth_getBalance",
                "eth_getTransactionCount",
                "eth_getStorageAt",
                "eth_newFilter",
                "eth_newBlockFilter",
                "eth_newPendingTransactionFilter",
                "eth_uninstallFilter",
                "eth_getLogs",
                "eth_accounts",
                "eth_signTypedData",
                "eth_coinbase"
        )
    )
    def test_api_response_validation(self, method):
        response = self.post(request_id=hex(77), method=method, params=self.test_data[method])
        assert response.status_code == 200, f"Got {response.status_code}, {response}"
        self.validate_schema(response=response, file_name=method)
