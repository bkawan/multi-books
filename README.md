
# Project Setup

## Setup

1. Copy environment file:

```bash
cp .env-example .env
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply database migrations:

```bash
python manage.py migrate
```

4. Import integration providers:

```bash
python manage.py import_integration_provider
```

## Run Project

1. Start Django server:

```bash
python manage.py runserver
```

2. Start Redis (required for Celery):

```bash
redis-server
```

3. Start Celery worker:

```bash
celery -A config worker --loglevel=info
```

## Environment Variables

Use `.env` to store sensitive info. Example values:

```
# QuickBooks Online
QBO_CLIENT_ID=RANDOM123CLIENTID456XYZ
QBO_CLIENT_SECRET=RANDOMSECRET789ABCDEF
QBO_REDIRECT_URI=http://localhost:8000/integration/quickbooks/callback
QBO_ENVIRONMENT=sandbox

# Zoho Books
ZOHO_CLIENT_ID=1000.RANDOMZOHOID123456
ZOHO_CLIENT_SECRET=RANDOMZOHOSECRET987654
ZOHO_REDIRECT_URI=http://localhost:8000/integration/zoho/callback
ZOHO_ENVIRONMENT=production
ZOHO_ACCOUNTS_BASE_URL=https://accounts.zoho.com
ZOHO_BOOKS_API_BASE_URL=https://books.zoho.com/api/v3

# Django
SECRET_KEY=randomdjangoSECRETkey1234567890
DEBUG=True
CUSTOM_FERNET_KEY="GENERATE_WITH_UTILS"
```

### Generate Fernet Key

To generate a secure `CUSTOM_FERNET_KEY`, run:

```bash
python utils/encryption.py
```

Replace the `CUSTOM_FERNET_KEY` value in `.env` with the generated key.


### QuickBooks API Endpoints

The following routes are available:

```

| Path                              | Description                     |
| --------------------------------- | ------------------------------- |
| `qbo/connect/<int:company_id>/`   | Connect a company to QuickBooks |
| `qbo/callback/`                   | QuickBooks OAuth callback       |
| `qbo/<int:company_id>/customers/` | Fetch customers from QuickBooks |
| `qbo/<int:company_id>/invoices/`  | Fetch invoices from QuickBooks  |

```
