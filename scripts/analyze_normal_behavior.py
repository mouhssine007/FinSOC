import json
from pathlib import Path


# -----------------------------
# 1. Define project paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "generated"


# -----------------------------
# 2. Load customers and transactions
# -----------------------------

with open(DATA_DIR / "customers.json", encoding="utf-8") as file:
    customers = json.load(file)

with open(DATA_DIR / "transactions.json", encoding="utf-8") as file:
    transactions = json.load(file)


# -----------------------------
# 3. Create an empty profile for each customer
# -----------------------------

customer_profiles = {}

for customer in customers:

    customer_id = customer["customer_id"]

    customer_profiles[customer_id] = {
        "customer_id": customer_id,
        "city": customer["city"],
        "account_type": customer["account_type"],
        "transaction_count": 0,
        "total_amount": 0.0,
        "amounts": [],
        "transaction_types": {},
        "statuses": {}
    }


# -----------------------------
# 4. Analyze every transaction
# -----------------------------

for transaction in transactions:

    customer_id = transaction["customer_id"]

    if customer_id not in customer_profiles:
        continue

    profile = customer_profiles[customer_id]

    amount = transaction["amount"]

    transaction_type = transaction["transaction_type"]

    status = transaction["status"]

    profile["transaction_count"] += 1

    profile["total_amount"] += amount

    profile["amounts"].append(amount)

    profile["transaction_types"][transaction_type] = (
        profile["transaction_types"].get(transaction_type, 0) + 1
    )

    profile["statuses"][status] = (
        profile["statuses"].get(status, 0) + 1
    )


# -----------------------------
# 5. Calculate customer statistics
# -----------------------------

for profile in customer_profiles.values():

    count = profile["transaction_count"]

    if count > 0:

        profile["average_amount"] = round(
            profile["total_amount"] / count, 2
        )

        profile["maximum_amount"] = round(
            max(profile["amounts"]), 2
        )

    else:

        profile["average_amount"] = 0

        profile["maximum_amount"] = 0

    profile["total_amount"] = round(
        profile["total_amount"], 2
    )

    del profile["amounts"]


# -----------------------------
# 6. Create final report
# -----------------------------

report = {
    "total_customers": len(customers),
    "total_transactions": len(transactions),
    "customer_profiles": list(customer_profiles.values())
}


# -----------------------------
# 7. Save report as JSON
# -----------------------------

output_file = DATA_DIR / "normal_behavior_summary.json"

with open(output_file, "w", encoding="utf-8") as file:

    json.dump(report, file, indent=4)


# -----------------------------
# 8. Display results
# -----------------------------

print("FinSOC NORMAL BEHAVIOR ANALYSIS")
print("--------------------------------")

print(f"Customers analyzed: {len(customers)}")

print(f"Transactions analyzed: {len(transactions)}")

print(f"Customer profiles created: {len(customer_profiles)}")

print(f"Report saved to: {output_file}")