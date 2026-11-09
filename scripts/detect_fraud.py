
import json
from pathlib import Path
from datetime import datetime, timedelta


# --------------------------------
# 1. Define project paths
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "generated"

OUTPUT_FILE = DATA_DIR / "fraud_alerts.json"


# --------------------------------
# 2. Load transaction data
# --------------------------------

def load_json(file_path):

    with open(file_path, encoding="utf-8") as file:
        return json.load(file)


normal_transactions = load_json(
    DATA_DIR / "transactions.json"
)

fraud_data = load_json(
    DATA_DIR / "fraud_scenarios.json"
)


# Extract transactions from the simulated scenarios
scenario_transactions = []

for scenario in fraud_data["scenarios"]:

    scenario_transactions.extend(
        scenario["transactions"]
    )


# Combine normal and simulated transactions
all_transactions = (
    normal_transactions + scenario_transactions
)


# --------------------------------
# 3. Build customer IP history
# --------------------------------

customer_ip_history = {}

for transaction in normal_transactions:

    customer_id = transaction["customer_id"]

    source_ip = transaction["source_ip"]

    if customer_id not in customer_ip_history:
        customer_ip_history[customer_id] = set()

    customer_ip_history[customer_id].add(source_ip)


# --------------------------------
# 4. Prepare alert storage
# --------------------------------

alerts = []


def create_alert(
    rule_id,
    alert_type,
    severity,
    customer_id,
    description,
    related_event_ids
):

    alert = {
        "alert_id": f"ALERT-{len(alerts) + 1:04d}",
        "rule_id": rule_id,
        "alert_type": alert_type,
        "severity": severity,
        "customer_id": customer_id,
        "description": description,
        "related_event_ids": related_event_ids,
        "status": "open"
    }

    alerts.append(alert)


# --------------------------------
# 5. Rule 1: High-value transactions
# --------------------------------

HIGH_VALUE_THRESHOLD = 40000

for transaction in all_transactions:

    if transaction["amount"] >= HIGH_VALUE_THRESHOLD:

        create_alert(
            rule_id="DET-001",
            alert_type="high_value_transaction",
            severity="high",
            customer_id=transaction["customer_id"],
            description=(
                f"Transaction amount "
                f"{transaction['amount']} MAD "
                f"reached the high-value threshold."
            ),
            related_event_ids=[transaction["event_id"]]
        )


# --------------------------------
# 6. Rule 2: Unusual IP addresses
# --------------------------------

for transaction in all_transactions:

    customer_id = transaction["customer_id"]

    source_ip = transaction["source_ip"]

    known_ips = customer_ip_history.get(
        customer_id, set()
    )

    if source_ip not in known_ips:

        create_alert(
            rule_id="DET-004",
            alert_type="unusual_ip_address",
            severity="medium",
            customer_id=customer_id,
            description=(
                f"Transaction received from unfamiliar "
                f"IP address: {source_ip}"
            ),
            related_event_ids=[transaction["event_id"]]
        )


# --------------------------------
# 7. Group transactions by customer
# --------------------------------

transactions_by_customer = {}

for transaction in all_transactions:

    customer_id = transaction["customer_id"]

    if customer_id not in transactions_by_customer:
        transactions_by_customer[customer_id] = []

    transactions_by_customer[customer_id].append(
        transaction
    )


# --------------------------------
# 8. Find suspicious transaction windows
# --------------------------------

def find_suspicious_window(
    customer_transactions,
    minimum_count,
    minutes,
    failed_only=False
):

    selected_transactions = []

    for transaction in customer_transactions:

        if failed_only and transaction["status"] != "failed":
            continue

        selected_transactions.append(transaction)

    selected_transactions.sort(
        key=lambda item: item["timestamp"]
    )

    for index, first_transaction in enumerate(
        selected_transactions
    ):

        start_time = datetime.fromisoformat(
            first_transaction["timestamp"].replace(
                "Z", "+00:00"
            )
        )

        matching_transactions = []

        for transaction in selected_transactions[index:]:

            transaction_time = datetime.fromisoformat(
                transaction["timestamp"].replace(
                    "Z", "+00:00"
                )
            )

            time_difference = (
                transaction_time - start_time
            )

            if time_difference <= timedelta(minutes=minutes):

                matching_transactions.append(transaction)

            else:
                break

        if len(matching_transactions) >= minimum_count:

            return matching_transactions

    return []


# --------------------------------
# 9. Rule 3: Rapid transactions
# --------------------------------

for customer_id, customer_transactions in (
    transactions_by_customer.items()
):

    rapid_transactions = find_suspicious_window(
        customer_transactions,
        minimum_count=5,
        minutes=10
    )

    if rapid_transactions:

        create_alert(
            rule_id="DET-002",
            alert_type="rapid_transactions",
            severity="high",
            customer_id=customer_id,
            description=(
                f"{len(rapid_transactions)} transactions "
                f"occurred within 10 minutes."
            ),
            related_event_ids=[
                transaction["event_id"]
                for transaction in rapid_transactions
            ]
        )


# --------------------------------
# 10. Rule 4: Repeated failed transactions
# --------------------------------

for customer_id, customer_transactions in (
    transactions_by_customer.items()
):

    failed_transactions = find_suspicious_window(
        customer_transactions,
        minimum_count=3,
        minutes=10,
        failed_only=True
    )

    if failed_transactions:

        create_alert(
            rule_id="DET-003",
            alert_type="repeated_failed_transactions",
            severity="medium",
            customer_id=customer_id,
            description=(
                f"{len(failed_transactions)} failed "
                f"transactions occurred within 10 minutes."
            ),
            related_event_ids=[
                transaction["event_id"]
                for transaction in failed_transactions
            ]
        )


# --------------------------------
# 11. Save alerts as JSON
# --------------------------------

alert_report = {
    "total_transactions_analyzed": len(all_transactions),
    "total_alerts": len(alerts),
    "alerts": alerts
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

    json.dump(alert_report, file, indent=4)


# --------------------------------
# 12. Display detection results
# --------------------------------

print("FinSOC FRAUD DETECTION ENGINE")
print("--------------------------------")

print(
    f"Transactions analyzed: {len(all_transactions)}"
)

print(f"Alerts generated: {len(alerts)}")

print("\nDETECTION RESULTS")

for alert in alerts:

    print(
        f"[{alert['severity'].upper()}] "
        f"{alert['rule_id']} - "
        f"{alert['alert_type']} - "
        f"{alert['customer_id']}"
    )

print("\nAlert report saved to:")
print(OUTPUT_FILE)
