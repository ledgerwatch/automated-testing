from web3 import Web3
from web3.middleware import geth_poa_middleware
import time

from tests.conftest import option


class MVPTestCase:
    def send_transaction(self, transaction):
        signed_transaction = self.web3.eth.account.sign_transaction(
            transaction, self.sender_private_key
        )

        transaction_hash = self.web3.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        ).hex()
        return transaction_hash

    def check_transaction_is_in_pool(self, transaction_hash):
        timeout = 10
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if transaction_hash in str(txpool):
                return
        raise AssertionError(f"Transaction {transaction_hash} is not in tx pool")

    def transaction_pool_is_empty(self):
        txpool = self.web3.geth.txpool.content()
        if len(txpool['pending']) == 0 and len(txpool['queued']) == 0:
            return True
        return False

    def wait_for_tx_pool_to_be_empty(self, timeout=60):
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if txpool['queued']:
                continue
            elif txpool['pending']:
                continue
            else:
                return
        raise TimeoutError(f"Transactions pool is not empty after {timeout} sec:\n{txpool}")

    def wait_for_transaction_to_be_removed_from_pool(self, transaction_hash, timeout=60):
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if transaction_hash in [tx['hash'] for p_value in txpool['queued'].values() for tx in p_value.values()]:
                continue
            elif [tx['hash'] for p_value in txpool['pending'].values() for tx in p_value.values()]:
                continue
            else:
                return
        raise TimeoutError(f"Transaction {transaction_hash} is in the tx pool after {timeout} sec")

    def setup_method(self):
        self.web3 = Web3(Web3.HTTPProvider(endpoint_uri=option.url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.sender_private_key = (
            0x26E86E45F6FC45EC6E2ECD128CEC80FA1D1505E5507DCD2AE58C3130A7A97B48
        )
        self.receiver_private_key = (
            0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8
        )
        self.sender_address = self.web3.eth.account.from_key(self.sender_private_key).address
        self.receiver_address = self.web3.eth.account.from_key(self.receiver_private_key).address

    def teardown_method(self):
        pass
