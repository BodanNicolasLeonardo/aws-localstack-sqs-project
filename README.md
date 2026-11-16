# AWS SQS cu LocalStack – Proiect Demo

## Descriere

Acest proiect demonstrează integrarea și utilizarea serviciului **AWS SQS (Simple Queue Service)** folosind **LocalStack** ca emulator local al serviciilor AWS și **Python (boto3)** ca SDK.

Scriptul `app.py` execută un ciclu complet de operațiuni pe o coadă SQS:
1. **Crearea** unei cozi SQS (`comenzi-magazin-queue`)
2. **Trimiterea** a 3 mesaje JSON reprezentând comenzi de magazin
3. **Citirea** mesajelor din coadă
4. **Consumarea** și **ștergerea** fiecărui mesaj folosind `ReceiptHandle`
5. **Verificarea** faptului că coada a rămas goală
6. **Ștergerea** cozii la final (cleanup)

---

## Cerințe preliminare

| Cerință | Versiune minimă | Verificare |
|---------|----------------|------------|
| **Docker** + Docker Compose | Docker 20+ | `docker --version` |
| **Python** | 3.8+ | `python --version` |
| **AWS CLI** (opțional, pentru comenzi manuale) | v2 | `aws --version` |

---

## Structura proiectului

```
aws-localstack-project/
├── docker-compose.yml    # Configurare LocalStack
├── requirements.txt      # Dependențe Python (boto3)
├── app.py                # Script principal – demo SQS
└── README.md             # Documentație (acest fișier)
```

---

## Instrucțiuni pas cu pas

### 1. Pornirea LocalStack

Deschide un terminal în directorul proiectului și rulează:

```bash
docker-compose up -d
```

Verifică statusul containerului:

```bash
docker ps
```

Ar trebui să vezi containerul `localstack-sqs` rulând pe portul `4566`.

### 2. Instalarea dependențelor Python

```bash
pip install -r requirements.txt
```

### 3. Rularea scriptului `app.py`

```bash
python app.py
```

Scriptul va afișa log-uri clare în consolă pentru fiecare pas executat.

### 4. Oprirea LocalStack

```bash
docker-compose down
```

---

## Comenzi AWS CLI pentru operațiuni manuale

Toate comenzile de mai jos folosesc `--endpoint-url=http://localhost:4566` pentru a comunica cu LocalStack în loc de AWS real.

### Creare coadă

```bash
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name comenzi-magazin-queue --region us-east-1
```

**Răspuns așteptat:**
```json
{
    "QueueUrl": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/comenzi-magazin-queue"
}
```

### Listare cozi existente

```bash
aws --endpoint-url=http://localhost:4566 sqs list-queues --region us-east-1
```

### Trimitere mesaj

**Bash / Linux / macOS:**
```bash
aws --endpoint-url=http://localhost:4566 sqs send-message \
    --queue-url http://localhost:4566/000000000000/comenzi-magazin-queue \
    --message-body '{"id": 1, "produs": "Laptop ASUS ROG", "cantitate": 1, "pret": 5499.99}' \
    --region us-east-1
```

**PowerShell (Windows):**
```powershell
$body = '{"id": 1, "produs": "Laptop ASUS ROG", "cantitate": 1, "pret": 5499.99}'
aws --endpoint-url=http://localhost:4566 sqs send-message --queue-url "http://localhost:4566/000000000000/comenzi-magazin-queue" --message-body $body --region us-east-1
```

### Citire mesaje

```bash
aws --endpoint-url=http://localhost:4566 sqs receive-message \
    --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/comenzi-magazin-queue \
    --max-number-of-messages 10 \
    --wait-time-seconds 5 \
    --region us-east-1
```

### Ștergere mesaj (folosind ReceiptHandle-ul primit la citire)

```bash
aws --endpoint-url=http://localhost:4566 sqs delete-message \
    --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/comenzi-magazin-queue \
    --receipt-handle "RECEIPT_HANDLE_PRIMIT_LA_CITIRE" \
    --region us-east-1
```

> **Notă:** Înlocuiește `RECEIPT_HANDLE_PRIMIT_LA_CITIRE` cu valoarea reală primită din comanda `receive-message`.

### Verificare atribute coadă (nr. mesaje)

```bash
aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes \
    --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/comenzi-magazin-queue \
    --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
    --region us-east-1
```

### Ștergere coadă

```bash
aws --endpoint-url=http://localhost:4566 sqs delete-queue \
    --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/comenzi-magazin-queue \
    --region us-east-1
```

---

## Concepte cheie SQS

| Concept | Descriere |
|---------|-----------|
| **Queue (Coadă)** | Structură FIFO care stochează mesaje temporar |
| **Producer** | Componenta care trimite mesaje în coadă |
| **Consumer** | Componenta care citește și procesează mesaje |
| **ReceiptHandle** | Token temporar primit la citirea unui mesaj, necesar pentru ștergere |
| **Visibility Timeout** | Perioadă în care un mesaj citit nu este vizibil altor consumatori |
| **Long Polling** | Tehnică de citire care așteaptă mesaje noi (reduce API calls goale) |

---

## Licență

Proiect educațional – fără restricții de utilizare.
