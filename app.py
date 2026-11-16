"""
AWS SQS Demo cu LocalStack
==========================
Script Python care demonstrează operațiunile CRUD pe o coadă SQS
folosind LocalStack ca emulator local al serviciilor AWS.
"""

import json
import boto3
import time

# ─── Configurare client SQS pentru LocalStack ────────────────────────────────
ENDPOINT_URL = "http://localhost:4566"
REGION = "us-east-1"
QUEUE_NAME = "comenzi-magazin-queue"

sqs = boto3.client(
    "sqs",
    endpoint_url=ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

# ─── Date de test: 3 comenzi reprezentate ca dicționare JSON ─────────────────
comenzi = [
    {"id": 1, "produs": "Laptop ASUS ROG", "cantitate": 1, "pret": 5499.99},
    {"id": 2, "produs": "Mouse Logitech MX Master 3", "cantitate": 2, "pret": 349.00},
    {"id": 3, "produs": "Tastatură Mechanică Cherry MX", "cantitate": 1, "pret": 699.50},
]


def separator(titlu: str) -> None:
    """Afișează un separator vizual în consolă."""
    print(f"\n{'='*60}")
    print(f"  {titlu}")
    print(f"{'='*60}")


def main():
    # ── Pasul 1: Crearea cozii SQS ──────────────────────────────────────────
    separator("PASUL 1: Crearea cozii SQS")
    response = sqs.create_queue(QueueName=QUEUE_NAME)
    queue_url = response["QueueUrl"]
    print(f"✅ Coada '{QUEUE_NAME}' a fost creată cu succes!")
    print(f"   Queue URL: {queue_url}")

    # ── Pasul 2: Trimiterea a 3 mesaje în coadă ─────────────────────────────
    separator("PASUL 2: Trimiterea mesajelor în coadă")
    for comanda in comenzi:
        body = json.dumps(comanda, ensure_ascii=False)
        resp = sqs.send_message(QueueUrl=queue_url, MessageBody=body)
        msg_id = resp["MessageId"]
        print(f"📤 Mesaj trimis  | ID: {msg_id}")
        print(f"   Conținut: {body}")
    print(f"\n✅ Total mesaje trimise: {len(comenzi)}")

    # Pauză scurtă pentru propagare
    time.sleep(1)

    # ── Pasul 3: Citirea mesajelor din coadă ─────────────────────────────────
    separator("PASUL 3: Citirea mesajelor din coadă")
    received = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
    )
    messages = received.get("Messages", [])
    print(f"📥 Mesaje primite: {len(messages)}")
    for msg in messages:
        body = json.loads(msg["Body"])
        print(f"   ─ Comanda #{body['id']}: {body['produs']} "
              f"(x{body['cantitate']}) – {body['pret']} RON")

    # ── Pasul 4: Consumarea și ștergerea fiecărui mesaj ──────────────────────
    separator("PASUL 4: Consumarea și ștergerea mesajelor")
    for msg in messages:
        body = json.loads(msg["Body"])
        receipt_handle = msg["ReceiptHandle"]
        # Simulăm procesarea comenzii
        print(f"⚙️  Procesez comanda #{body['id']}: {body['produs']}...")
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print(f"🗑️  Mesaj șters din coadă (ReceiptHandle: {receipt_handle[:40]}...)")
    print(f"\n✅ Toate cele {len(messages)} mesaje au fost procesate și șterse.")

    # ── Pasul 5: Verificarea faptului că coada este goală ────────────────────
    separator("PASUL 5: Verificarea cozii (trebuie să fie goală)")
    time.sleep(1)
    attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
        ],
    )
    visible = attrs["Attributes"]["ApproximateNumberOfMessages"]
    not_visible = attrs["Attributes"]["ApproximateNumberOfMessagesNotVisible"]
    print(f"   Mesaje vizibile:     {visible}")
    print(f"   Mesaje ne-vizibile:  {not_visible}")
    if visible == "0" and not_visible == "0":
        print("✅ Coada este goală – toate mesajele au fost consumate!")
    else:
        print("⚠️  Coada nu este complet goală.")

    # ── Pasul 6: Ștergerea cozii (cleanup) ───────────────────────────────────
    separator("PASUL 6: Ștergerea cozii (cleanup)")
    sqs.delete_queue(QueueUrl=queue_url)
    print(f"🗑️  Coada '{QUEUE_NAME}' a fost ștearsă cu succes!")

    separator("DEMO FINALIZAT CU SUCCES 🎉")


if __name__ == "__main__":
    main()
