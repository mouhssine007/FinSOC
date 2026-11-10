
import json
from confluent_kafka import Consumer, KafkaException

config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "finsoc-consumer-group",
    "auto.offset.reset": "earliest"
}

consumer = Consumer(config)

TOPIC = "transactions"


def main():

    consumer.subscribe([TOPIC])

    print("FinSOC Consumer started...")
    print("Waiting for financial events...\n")

    try:
        while True:

            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            event = json.loads(message.value().decode("utf-8"))

            print("=" * 40)
            print("TRANSACTION RECEIVED")
            print("Event ID:", event.get("event_id"))
            print("Customer:", event.get("customer_id"))
            print("Amount:", event.get("amount"))
            print("Timestamp:", event.get("timestamp"))

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
