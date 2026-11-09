import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "data/schemas/transaction.schema.json") as file:
    schema = json.load(file)

with open(BASE_DIR / "data/samples/transactions.json") as file:
    transactions = json.load(file)

# Simulate corrupted transaction data
transactions[0]["amount"] = 0

validator = Draft202012Validator(
    schema,
    format_checker=FormatChecker()
)

errors = list(validator.iter_errors(transactions[0]))

if errors:
    print("INVALID TRANSACTION DETECTED!")

    for error in errors:
        print("Reason:", error.message)
else:
    print("Transaction is VALID")