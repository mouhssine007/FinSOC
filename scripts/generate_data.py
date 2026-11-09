import json
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Make random results reproducible
random.seed(42)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# 1. Generate fictional customers
# -----------------------------

first_names = [
    "Youssef", "Amine", "Omar", "Karim", "Hamza",
    "Salma", "Sara", "Nadia", "Imane", "Meryem"
]

last_names = [
    "Alaoui", "Bennani", "Tazi", "Idrissi", "Amrani",
    "Fassi", "Berrada", "Chraibi", "Mansouri", "Naciri"
]

cities = [
    "Casablanca", "Rabat", "Marrakech",
    "Fes", "Tangier", "Agadir"
]

account_types = ["checking", "savings"]

customers = []

for number in range(1, 101):

    customer = {
        "customer_id": f"CUST-{number:04d}",
        "first_name": random.choice(first_names),
        "last_name": random.choice(last_names),
        "city": random.choice(cities),
        "account_type": random.choice(account_types)
    }

    customers.append(customer)


# -----------------------------
# 2. Generate financial transactions
# -----------------------------

transaction_types = [
    "deposit",
    "withdrawal",
    "transfer",
    "payment"
]

statuses = [
    "success",
    "failed",
    "pending"
]

source_ips = [
    "192.0.2.10",
    "198.51.100.15",
    "203.0.113.20",
    "192.0.2.25",
    "198.51.100.30"
]

transactions = []

start_time = datetime(
    2026, 11, 9, 9, 0, 0,
    tzinfo=timezone.utc
)

for number in range(1, 1001):

    transaction_type = random.choice(transaction_types)

    transaction = {
        "event_id": f"EVT-TXN-{number:04d}",
        "event_type": "transaction",
        "timestamp": (
            start_time + timedelta(minutes=number)
        ).isoformat().replace("+00:00", "Z"),
        "transaction_id": f"TXN-{number:05d}",
        "customer_id": random.choice(customers)["customer_id"],
        "transaction_type": transaction_type,
        "amount": round(random.uniform(10, 50000), 2),
        "currency": "MAD",
        "status": random.choice(statuses),
        "source_ip": random.choice(source_ips)
    }

    if transaction_type == "transfer":
        transaction["destination_account_id"] = (
            f"ACC-{random.randint(1, 100):03d}"
        )

    transactions.append(transaction)


# -----------------------------
# 3. Save data as JSON files
# -----------------------------

with open(
    OUTPUT_DIR / "customers.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(customers, file, indent=4)


with open(
    OUTPUT_DIR / "transactions.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(transactions, file, indent=4)


# -----------------------------
# 4. Display generation results
# -----------------------------

print("FinSOC DATA GENERATION COMPLETED")
print("--------------------------------")
print(f"Customers generated: {len(customers)}")
print(f"Transactions generated: {len(transactions)}")
print(f"Output directory: {OUTPUT_DIR}")