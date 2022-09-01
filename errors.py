import random

wrong_payload_errors_legacy = [
    {
        "fields": {"gas": 1.0},
        "error": "Transaction had invalid fields: {'gas': 1.0}"
    },
    {
        "fields": {"gas": "test"},
        "error": "Transaction had invalid fields: {'gas': 'test'}"
    },
    {
        "fields": {"gas": [1]},
        "error": "Transaction had invalid fields: {'gas': [1]}"
    }
]

wrong_payload_errors_eip1559 = wrong_payload_errors_legacy.copy()
# noinspection PyTypeChecker
wrong_payload_errors_eip1559.extend(
    (
        {
            "fields": {"maxFeePerGas": 1.0},
            "error": "Transaction had invalid fields: {'maxFeePerGas': 1.0}"
        },
        {
            "fields": {"maxFeePerGas": 'test'},
            "error": "Transaction had invalid fields: {'maxFeePerGas': 'test'}"
        },
        {
            "fields": {"maxFeePerGas": [1]},
            "error": "Transaction had invalid fields: {'maxFeePerGas': [1]}"
        },
        {
            "fields": {"maxPriorityFeePerGas": "test"},
            "error": "Transaction had invalid fields: {'maxPriorityFeePerGas': 'test'}"
        }
    )
)

chain_id = random.randint(2000, 100000)

wrong_fields_errors_common = [
    {
        "fields": {"chainId": chain_id},
        "error": f'INTERNAL_ERROR: rlp parse transaction: invalid chainID, {chain_id} (expected 1337)'
    }
]
for i in [0, 1, 10000, 20199]:
    wrong_fields_errors_common.append(
        {
            "fields": {"gas": i},
            "error": 'INTERNAL_ERROR: IntrinsicGas'
        }
    )

wrong_fields_errors_legacy = [

]

wrong_fields_errors_eip1559 = [
    {
        "fields": {"maxFeePerGas": 0},
        "error": 'FEE_TOO_LOW: fee too low'
    },
    {
        "fields": {"maxFeePerGas": 6},
        "error": 'FEE_TOO_LOW: fee too low'
    }
]

# maxPriorityFee ={
#     "test: ""Transaction is sent with gas value = 'test'"
# }
