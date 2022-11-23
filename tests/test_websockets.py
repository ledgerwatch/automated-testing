import logging

import pytest

from tests.websocket_test_case import WebSocketTestCase
from transaction_templates import TransactionTemplates


class TestWebSocketTestCase(WebSocketTestCase):

    def _create_transactions(self):
        successful_transactions = list()
        nonce = self.web3.eth.get_transaction_count(self.sender_address)
        for tx_count in range(20):
            transaction_dict = TransactionTemplates.legacy_transaction(
                self.web3, self.receiver_address, self.sender_private_key
            )
            transaction_dict["nonce"] = nonce + tx_count + 1
            transaction_hash = self.send_transaction(transaction_dict)
            successful_transactions.append(transaction_hash)
        successful_transactions.append(
            self.send_transaction(
                TransactionTemplates.legacy_transaction(
                    self.web3, self.receiver_address, self.sender_private_key
                )
            )
        )
        for transaction_hash in successful_transactions:
            assert self.transaction_is_removed_from_pool(
                transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"
        return successful_transactions

    @pytest.mark.smoke_test
    def test_eth_subscribe(self):
        subscription_results, transactions = self.create_connection(
            functions=[
                self.eth_subscribe,
                self._create_transactions
            ]
        )
        logging.info(f"Created transactions: {transactions}")
        logging.info(f"Got subscription results: {subscription_results}")
        subs_id = subscription_results[0][0]
        for res in subscription_results[0][1]:
            assert res['params']['subscription'] == subs_id
