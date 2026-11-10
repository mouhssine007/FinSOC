
import json
from pathlib import Path
from confluent_kafka import Producer

# Project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Generated transaction data
DATA_FILE = BASE_DIR / "data" / "generated" / "transactions.json"

# Redpanda connection
config = {
    "bootstrap.servers": "localhost:9092"
}

producer = Producer(config)

TOPIC = "transactions"


def delivery_report(err, message):
    """Report whether a message was delivered."""

    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Delivered to {message.topic()} "
            f"[partition {message.partition()}]"
        )


def main():

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        transactions = json.load(file)

    # Send only 10 events for the first test
    for transaction in transactions[:10]:

        producer.produce(
            TOPIC,
            key=str(transaction.get("event_id", "")),
            value=json.dumps(transaction),
            callback=delivery_report
        )

        producer.poll(0)

    # Wait until all messages are delivered
    remaining = producer.flush(10)

    if remaining:
        print(f"{remaining} messages were not delivered.")
    else:
        print("All test transactions were sent successfully.")


if __name__ == "__main__":
    main()
