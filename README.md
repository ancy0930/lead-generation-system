# UAE Lead Management System SaaS

Welcome to the UAE Lead Management System! The project is an enterprise-grade, Multi-tenant CRM that incorporates JWT Authentication, Celery asynchronous notifications, Redis caching, robust structured logging, and an advanced Metrics API. 

Here is how you can spin up the project locally.

## Method 1: Using Docker (Recommended)
Docker handles spinning up the Redis cache server, the Celery worker, and the Django Application exactly as it would run in Production.

1. Ensure **Docker Desktop** is installed and running on your system.
2. Open your terminal at `c:\Users\lenovo\Desktop\lead generation system`
3. Run the following command:
   ```bash
   docker-compose up --build
   ```
4. Once the containers are built and running, your application is available at:
   - **Frontend / Landing Page**: `http://localhost:8000/`
   - **Admin Dashboard**: `http://localhost:8000/admin/`

## Method 2: Running Natively Locally (Windows / PowerShell)

If you prefer to run it using Python directly without Docker, follow these steps:

### 1. Requirements & Setup
First, activate the virtual environment and ensure all dependencies are installed:
```powershell
# Open powershell in the project folder
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Redis Setup (Required for Celery & Caching)
Because we migrated into an enterprise structure, a Redis server must be active on `localhost:6379`.
If you do not have Redis installed natively on Windows (which is tricky), you can quickly spin one up using Docker:
```powershell
docker run -p 6379:6379 -d redis:7-alpine
```

### 3. Start the Django Server
Run standard migrations (already done, but good practice) and boot the main web server:
```powershell
python manage.py migrate
python manage.py runserver
```
Your site now lives at `http://127.0.0.1:8000/`.

### 4. Start the Celery Worker (New Terminal Window)
To process the automatic WhatsApp and Email notifications, you must spin up the Celery worker.
Open **a new PowerShell window** inside your project folder:
```powershell
.\venv\Scripts\Activate.ps1
celery -A core worker -l info --pool=solo
```
*(Note: `--pool=solo` is specifically required when running Celery natively on Windows machines; Docker does not need this limitation).*

---

## Testing the System
1. Go to `http://127.0.0.1:8000/` and submit a new lead.
2. Watch your terminal running the **Celery Worker**. It will catch the signal, pause (to simulate network latency), and output the structured JSON log and notification trace (WhatsApp / Email).
3. Log into the `http://127.0.0.1:8000/admin/` using your superuser credentials (`admin` / `admin`).
4. Click on **Leads** and switch the status to `Contacted`.
5. Check your database / metrics endpoint: `http://127.0.0.1:8000/api/leads/metrics/` to see the analytical calculations updating beautifully! 
