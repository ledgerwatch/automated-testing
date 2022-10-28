import math

import pytest

from contract_templates import ContractHelper
from errors import (
    wrong_payload_errors_legacy,
    wrong_payload_errors_eip1559,
    wrong_fields_errors_common,
    wrong_fields_errors_legacy,
    wrong_fields_errors_eip1559,
)
from tests import generate_tests, form_template
from tests.base_test_case import MVPTestCase
from transaction_templates import TransactionTemplates


class TestMVPTestCase(MVPTestCase):
    @pytest.mark.parametrize(
        "number_of_transactions",
        [
            1, 10, 300
        ],
    )
    @pytest.mark.parametrize(
        "transaction_template",
        [
            TransactionTemplates.legacy_transaction,
            TransactionTemplates.eip1559_transaction,
        ],
    )
    @pytest.mark.smoke_test
    def test_batch_of_valid_transactions(self, number_of_transactions, transaction_template):
        successful_transactions = list()
        initial_block = self.web3.eth.get_block("latest", False)

        nonce = self.web3.eth.get_transaction_count(self.sender_address)

        # to put batch of transactions into queue we send them with nonce+1 or more

        for tx_count in range(number_of_transactions - 1):
            transaction_dict = transaction_template(
                self.web3, self.receiver_address, self.sender_private_key
            )
            transaction_dict["nonce"] = nonce + tx_count + 1
            transaction_hash = self.send_transaction(transaction_dict)

            successful_transactions.append(transaction_hash)

        # sending transaction with the latest nonce automatically attaches all the rest

        successful_transactions.append(
            self.send_transaction(
                transaction_template(
                    self.web3, self.receiver_address, self.sender_private_key
                )
            )
        )
        assert len(successful_transactions) == number_of_transactions

        # check no transactions left in transaction pool
        for transaction_hash in successful_transactions:
            assert self.transaction_is_removed_from_pool(
                transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"

        # verify if batch of transactions fits into expected number of blocks
        latest_block_number = self.web3.eth.get_block("latest", False)
        blocks_to_fit_transactions = math.ceil(
            number_of_transactions / (initial_block["gasLimit"] / 21000)
        )
        blocks_diff = latest_block_number["number"] - initial_block["number"]

        assert blocks_diff >= blocks_to_fit_transactions, (
            f"It took {blocks_diff} to fit {number_of_transactions} "
            f"while {blocks_to_fit_transactions} blocks required"
        )

    @pytest.mark.parametrize(
        "transaction_template",
        [
            TransactionTemplates.legacy_transaction,
            TransactionTemplates.eip1559_transaction,
        ],
    )
    def test_transaction_type(self, transaction_template):

        transaction_hash = self.send_transaction(
            transaction_template(
                self.web3, self.receiver_address, self.sender_private_key
            )
        )
        assert self.transaction_is_in_pool(transaction_hash), f"Transaction {transaction_hash} is not in tx pool"
        assert self.transaction_is_removed_from_pool(
            transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"

    @pytest.mark.parametrize(
        "gas, status",
        [(200000, 0), (5000000, 1)],  # failed contract  # successful contract
    )
    def test_transaction_contract_deployment(self, gas, status):
        transaction_hash = self.send_transaction(
            ContractHelper.deploy_contract(
                web3=self.web3,
                private_key=self.sender_private_key,
                contract_path="/ERC20_token.sol",
                contract_name="MySimpleToken",
                gas=gas,
                token_name="SERGEY2",
                token_symbol="SRG2"
            )
        )
        assert self.transaction_is_removed_from_pool(
            transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"
        assert (
                self.web3.eth.get_transaction_receipt(transaction_hash)["status"] == status
        ), f"Transaction status expected to be {status}"

    @pytest.mark.parametrize(
        "contract_path, contract_name, token_name, token_symbol, amount", [
            ("/ERC20_token.sol", "MySimpleToken", "SERGEY2", "SRG2", 100),
            ("/ERC721.sol", "MyNFT", None, None, 1)
        ]
    )
    def test_transaction_send_tokens(self, contract_path, contract_name, token_name, token_symbol, amount):
        transaction_hash = self.send_transaction(
            ContractHelper.deploy_contract(
                web3=self.web3,
                private_key=self.sender_private_key,
                contract_path=contract_path,
                contract_name=contract_name,
                gas=5000000,
                token_name=token_name,
                token_symbol=token_symbol
            )
        )

        assert self.transaction_is_removed_from_pool(
            transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"
        signed_txn = self.web3.eth.get_transaction_receipt(transaction_hash)
        assert (
                signed_txn["status"] == 1
        ), f"Transaction status is expected to be 1 but was 0 in {signed_txn}"

        deployed_contract_address = self.web3.eth.get_transaction_receipt(transaction_hash)["contractAddress"]
        abi = ContractHelper.compile_contract(contract_path=contract_path, contract_name=contract_name)["abi"]

        contract = self.web3.eth.contract(deployed_contract_address, abi=abi)

        sender_balance_before = contract.functions.balanceOf(self.sender_address).call()
        receiver_balance_before = contract.functions.balanceOf(
            self.receiver_address
        ).call()

        if "ERC20" in contract_path:
            data = contract.encodeABI("transfer", args=(self.receiver_address, amount))
        else:
            data = contract.encodeABI("transferFrom", args=(
                self.sender_address, self.receiver_address, contract.functions.tokenId().call()))

        raw_txn = {
            "from": self.sender_address,
            "gasPrice": self.web3.eth.gas_price,
            "gas": 6000000,
            "to": deployed_contract_address,
            "value": "0x0",
            "data": data,
            "nonce": self.web3.eth.getTransactionCount(self.sender_address),
            "chainId": self.web3.eth.chain_id,
        }

        signed_txn = self.web3.eth.account.signTransaction(
            raw_txn, self.sender_private_key
        )
        sent_transaction = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        token_transaction_hash = sent_transaction.hex()

        assert self.transaction_is_removed_from_pool(
            token_transaction_hash), f"Transaction {transaction_hash} is not removed from the tx pool"
        assert (
                self.web3.eth.get_transaction_receipt(token_transaction_hash)["status"] == 1
        ), f"Transaction status is expected to be 1 but was 0 in {signed_txn}, tx body sent {raw_txn}"

        sender_balance_after = contract.functions.balanceOf(self.sender_address).call()
        assert sender_balance_after == (sender_balance_before - amount), (
            f"Sender address {self.sender_address} balance was {sender_balance_before} "
            f"but is {sender_balance_after} after transaction has been mined"
        )

        receiver_balance_after = contract.functions.balanceOf(
            self.receiver_address
        ).call()
        assert receiver_balance_after == (receiver_balance_before + amount), (
            f"Receiver address {self.receiver_address} balance was {receiver_balance_before} "
            f"but is {receiver_balance_after} after transaction has been mined"
        )

    @pytest.mark.parametrize(
        "transaction_template,data_set",
        generate_tests(
            template_1=TransactionTemplates.legacy_transaction,
            template_2=TransactionTemplates.eip1559_transaction,
            test_data_1=wrong_fields_errors_common + wrong_fields_errors_legacy,
            test_data_2=wrong_fields_errors_common + wrong_fields_errors_eip1559,
        ),
    )
    def test_transaction_with_wrong_field_values(self, transaction_template, data_set):
        template = form_template(
            transaction_template=transaction_template(
                self.web3, self.receiver_address, self.sender_private_key
            ),
            fields_to_update=data_set["fields"],
        )
        try:
            self.send_transaction(template)
            raise AssertionError(
                f"Transaction is sent with fields: {data_set['fields']}"
            )
        except ValueError as e:
            assert all(
                (e.args[0]["code"] == -32000, e.args[0]["message"] == data_set["error"])
            ), f"Got error {str(e)}"
        assert self.tx_pool_is_empty(timeout=5), "Transactions pool is not empty after 5 sec"

    @pytest.mark.parametrize(
        "transaction_template,data_set",
        generate_tests(
            template_1=TransactionTemplates.legacy_transaction,
            template_2=TransactionTemplates.eip1559_transaction,
            test_data_1=wrong_payload_errors_legacy,
            test_data_2=wrong_payload_errors_eip1559,
        ),
    )
    def test_transaction_wrong_payload(self, transaction_template, data_set):
        template = form_template(
            transaction_template=transaction_template(
                self.web3, self.receiver_address, self.sender_private_key
            ),
            fields_to_update=data_set["fields"],
        )
        try:
            self.send_transaction(template)
            raise AssertionError(
                f"Transaction is sent with fields:  {data_set['fields']}"
            )
        except TypeError as e:
            assert str(e) == data_set["error"]

    @pytest.mark.parametrize("transaction_template",
                             [TransactionTemplates.legacy_transaction])
    def test_replace_transaction(self, transaction_template):

        transaction_template_low_gas_price = transaction_template(self.web3,
                                                                  self.receiver_address,
                                                                  self.sender_private_key)

        transaction_template_low_gas_price.update(
            {"gasPrice": int(self.web3.eth.gas_price / 1000)}
        )
        low_gas_price_txn_hash = self.send_transaction(transaction_template_low_gas_price)
        low_gas_price_txn_nonce = self.web3.eth.get_transaction(low_gas_price_txn_hash)["nonce"]

        assert low_gas_price_txn_hash in str(self.web3.geth.txpool.content())

        transaction_template_low_gas_price.update(
            {"gasPrice": int(self.web3.eth.gas_price * 3),
             "nonce": low_gas_price_txn_nonce})

        replacing_txn_hash = self.send_transaction(transaction_template_low_gas_price)

        assert low_gas_price_txn_hash not in str(self.web3.geth.txpool.content())
        assert self.transaction_is_removed_from_pool(
            replacing_txn_hash), f"Transaction {replacing_txn_hash} is not removed from the tx pool"
