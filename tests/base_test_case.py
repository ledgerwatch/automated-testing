import time

from web3 import Web3
from web3.middleware import geth_poa_middleware

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

    def transaction_is_in_pool(self, transaction_hash) -> bool:
        timeout = 10
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if transaction_hash in str(txpool):
                return True
        return False

    def transaction_pool_is_empty(self):
        txpool = self.web3.geth.txpool.content()
        if len(txpool["pending"]) == 0 and len(txpool["queued"]) == 0:
            return True
        return False

    def tx_pool_is_empty(self, timeout=60) -> bool:
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if txpool["queued"]:
                continue
            elif txpool["pending"]:
                continue
            else:
                return True
        return False

    def transaction_is_removed_from_pool(self, transaction_hash, timeout=60) -> bool:
        start_time = time.time()
        while time.time() - start_time <= timeout:
            txpool = self.web3.geth.txpool.content()
            if transaction_hash in [
                tx["hash"]
                for p_value in txpool["queued"].values()
                for tx in p_value.values()
            ]:
                continue
            elif [
                tx["hash"]
                for p_value in txpool["pending"].values()
                for tx in p_value.values()
            ]:
                continue
            else:
                return True
        return False

    def setup_method(self):
        self.web3 = Web3(Web3.HTTPProvider(endpoint_uri=option.url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.sender_private_key = (
            0x26E86E45F6FC45EC6E2ECD128CEC80FA1D1505E5507DCD2AE58C3130A7A97B48
        )
        self.receiver_private_key = (
            0x45A915E4D060149EB4365960E6A7A45F334393093061116B197E3240065FF2D8
        )
        self.sender_address = self.web3.eth.account.from_key(
            self.sender_private_key
        ).address
        self.receiver_address = self.web3.eth.account.from_key(
            self.receiver_private_key
        ).address

    def teardown_method(self):
        pass
