import os

contracts_path = os.environ.get("MOCKS_DIR", f"{os.path.dirname(__file__)}/Contracts")


class TransactionTemplates:
    @staticmethod
    def base_template(web3, address, private_key):
        return {
            "nonce": web3.eth.get_transaction_count(
                web3.eth.account.from_key(private_key).address
            ),
            "to": address,
            "value": web3.toWei(0.02, "ether"),
            "gas": 21000,
            "chainId": web3.eth.chain_id,
        }

    @staticmethod
    def legacy_transaction(web3, address, private_key):
        legacy_transaction = TransactionTemplates.base_template(
            web3, address, private_key
        ).copy()
        legacy_transaction.update(
            {
                "gasPrice": web3.eth.gas_price,
            }
        )
        return legacy_transaction

    @staticmethod
    def eip1559_transaction(web3, address, private_key):
        eip1559_transaction = TransactionTemplates.base_template(
            web3, address, private_key
        ).copy()

        max_priority_fee = web3.eth.max_priority_fee
        max_fee_per_gas = max_priority_fee + web3.eth.get_block("latest").baseFeePerGas

        eip1559_transaction.update(
            {"maxFeePerGas": max_fee_per_gas, "maxPriorityFeePerGas": max_priority_fee}
        )
        return eip1559_transaction
