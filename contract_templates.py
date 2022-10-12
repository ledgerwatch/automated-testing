import os

import solcx

contracts_path = os.environ.get("MOCKS_DIR", f"{os.path.dirname(__file__)}/Contracts")


class ContractHelper:
    @staticmethod
    def compile_contract(contract_path, contract_name):
        def compile_source_file():
            solcx.install_solc("0.8.13")
            with open(contracts_path + contract_path, "r", encoding="utf-8") as f:
                return solcx.compile_source(
                    f.read(), output_values=["abi", "bin"], solc_version="0.8.13"
                )

        contract_interface = compile_source_file()[
            f"<stdin>:{contract_name}"
        ]  # Compiled source code
        return {
            "abi": contract_interface["abi"],
            "bytecode": contract_interface["bin"],
        }

    @staticmethod
    def deploy_contract(
            web3, private_key, contract_path, contract_name, gas=5000000, token_name=None, token_symbol=None
    ):
        abi_bytecode = ContractHelper.compile_contract(contract_path, contract_name)
        contract_ = web3.eth.contract(
            abi=abi_bytecode["abi"],
            bytecode=abi_bytecode["bytecode"],
        )
        account = web3.eth.account.privateKeyToAccount(private_key)
        if token_name and token_symbol:
            contract_constructor = contract_.constructor(token_name, token_symbol)
        else:
            contract_constructor = contract_.constructor()
        return contract_constructor.buildTransaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": gas,
                "gasPrice": web3.eth.gas_price,
            }
        )
