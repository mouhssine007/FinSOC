import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

BASE_DIR = Path(__file__).parent


def validate_file(schema_path, data_path):
    with open(BASE_DIR / schema_path, encoding="utf-8") as file:
        schema = json.load(file)

    with open(BASE_DIR / data_path, encoding="utf-8") as file:
        records = json.load(file)

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker()
    )

    errors_found = 0

    for index, record in enumerate(records):
        errors = list(validator.iter_errors(record))

        if errors:
            errors_found += len(errors)
            print(f"\nRecord {index + 1}: INVALID")

            for error in errors:
                print(f" - {error.message}")
        else:
            print(f"Record {index + 1}: VALID")

    print(f"\nTotal records: {len(records)}")
    print(f"Validation errors: {errors_found}")

    return errors_found == 0


if __name__ == "__main__":

    print("=== TRANSACTION VALIDATION ===")

    transactions_valid = validate_file(
        "data/schemas/transaction.schema.json",
        "data/samples/transactions.json"
    )

    print("\n=== AUTHENTICATION VALIDATION ===")

    authentication_valid = validate_file(
        "data/schemas/authentication.schema.json",
        "data/samples/authentication_events.json"
    )

    if transactions_valid and authentication_valid:
        print("\nSUCCESS: All records passed validation.")
    else:
        print("\nFAILED: Some records contain errors.")