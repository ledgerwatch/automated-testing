def generate_tests(template_1, template_2, test_data_1, test_data_2):
    return [(template_1, i) for i in test_data_1] + [
        (template_2, i) for i in test_data_2
    ]


def form_template(transaction_template: dict, fields_to_update: dict):
    for key, value in fields_to_update.items():
        transaction_template[key] = value
    return transaction_template
