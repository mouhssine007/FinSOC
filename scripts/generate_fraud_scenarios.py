
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone


# --------------------------------
# 1. Define project paths
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "generated"

OUTPUT_FILE = DATA_DIR / "fraud_scenarios.json"


# --------------------------------
# 2. Load generated customers
# --------------------------------

with open(DATA_DIR / "customers.json", encoding="utf-8") as file:
    customers = json.load(file)

customer_ids = [
    customer["customer_id"]
    for customer in customers
]


# --------------------------------
# 3. Create a transaction generator
# --------------------------------

def create_transaction(
    number,
    customer_id,
    amount,
    transaction_type,
    status,
    source_ip,
    timestamp
):

    transaction = {
        "event_id": f"EVT-FRAUD-{number:04d}",
        "event_type": "transaction",
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "transaction_id": f"FRAUD-TXN-{number:04d}",
        "customer_id": customer_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "currency": "MAD",
        "status": status,
        "source_ip": source_ip
    }

    if transaction_type == "transfer":
        transaction["destination_account_id"] = "ACC-999"

    return transaction


# --------------------------------
# 4. Define scenario customers
# --------------------------------

customer_high_value = customer_ids[0]
customer_rapid = customer_ids[1]
customer_failed = customer_ids[2]
customer_unusual_ip = customer_ids[3]


base_time = datetime(
    2026, 11, 9, 12, 0, 0,
    tzinfo=timezone.utc
)


# --------------------------------
# 5. Create suspicious scenarios
# --------------------------------

scenarios = []


# Scenario 1: High-value transaction

high_value_transaction = create_transaction(
    1,
    customer_high_value,
    49999.00,
    "transfer",
    "success",
    "192.0.2.10",
    base_time
)

scenarios.append({
    "scenario_id": "FRAUD-001",
    "scenario_type": "high_value_transaction",
    "description": "A customer makes an unusually large transaction.",
    "transactions": [high_value_transaction]
})


# Scenario 2: Multiple rapid transactions

rapid_transactions = []

for number in range(2, 7):

    transaction = create_transaction(
        number,
        customer_rapid,
        2000.00,
        "payment",
        "success",
        "198.51.100.15",
        base_time + timedelta(minutes=number)
    )

    rapid_transactions.append(transaction)


scenarios.append({
    "scenario_id": "FRAUD-002",
    "scenario_type": "rapid_transactions",
    "description": "Five transactions occur within a short time.",
    "transactions": rapid_transactions
})


# Scenario 3: Repeated failed transactions

failed_transactions = []

for number in range(7, 11):

    transaction = create_transaction(
        number,
        customer_failed,
        1500.00,
        "withdrawal",
        "failed",
        "203.0.113.20",
        base_time + timedelta(minutes=number)
    )

    failed_transactions.append(transaction)


scenarios.append({
    "scenario_id": "FRAUD-003",
    "scenario_type": "repeated_failed_transactions",
    "description": "A customer has four failed transactions.",
    "transactions": failed_transactions
})


# Scenario 4: Unusual IP address

unusual_ip_transaction = create_transaction(
    11,
    customer_unusual_ip,
    8000.00,
    "transfer",
    "success",
    "203.0.113.250",
    base_time + timedelta(minutes=15)
)

scenarios.append({
    "scenario_id": "FRAUD-004",
    "scenario_type": "unusual_ip_address",
    "description": "A transaction comes from an unfamiliar IP address.",
    "transactions": [unusual_ip_transaction]
})


# --------------------------------
# 6. Save fraud scenarios
# --------------------------------

output_data = {
    "description": "Synthetic fraud scenarios for SOC detection practice.",
    "scenario_count": len(scenarios),
    "scenarios": scenarios
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(output_data, file, indent=4)


# --------------------------------
# 7. Display results
# --------------------------------

total_transactions = sum(
    len(scenario["transactions"])
    for scenario in scenarios
)

print("FinSOC FRAUD SCENARIOS GENERATED")
print("--------------------------------")

print(f"Scenarios created: {len(scenarios)}")

print(f"Suspicious transactions: {total_transactions}")

print(f"Output file: {OUTPUT_FILE}")

print("\nScenario types:")

for scenario in scenarios:
    print("-", scenario["scenario_type"])
