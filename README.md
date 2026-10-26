# Expense Tracker - Django REST Framework Backend

Production-ready, modular REST API built with **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, **Simple JWT**, and **django-cors-headers**, custom-tailored to power the Expense Tracker React + Vite frontend.

---

## 📁 1. Project Structure

```text
backend/
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo_data.py
│   └── migrations/
│       └── 0001_initial.py
├── transactions/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│       └── 0001_initial.py
├── categories/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── utils.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│       └── 0001_initial.py
└── budgets/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    └── migrations/
        └── 0001_initial.py
```

---

## 🛠️ 2. Technology Stack

* **Python 3.12+**
* **Django 5.1+**
* **Django REST Framework (DRF)**: Web API toolkit
* **djangorestframework-simplejwt**: Industry-standard JSON Web Token (JWT) authentication
* **PostgreSQL**: Robust relational database (with `psycopg2-binary`)
* **django-cors-headers**: Cross-Origin Resource Sharing handling for Vite React (`http://localhost:5173`)
* **python-dotenv**: Environment variable management
* **django-filter**: Flexible querying for transaction search and sorting

---

## ⚙️ 3. Environment Variables Configuration

Copy `.env.example` to `.env` or update `.env`:

```ini
SECRET_KEY=django-insecure-expense-tracker-prod-ready-secret-key-2024
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DATABASE_NAME=expense_tracker_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# CORS Allowed Origins
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional: Set to True for instant zero-dependency testing without a running PostgreSQL server
USE_SQLITE=False
```

---

## 🚀 4. Setup & Installation

### Step 1: Activate Virtual Environment
On Windows (PowerShell):
```powershell
# From the backend directory or workspace root:
..\.venv\Scripts\Activate.ps1
```

Or create a new one:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Create PostgreSQL Database
In your PostgreSQL console (`psql` or pgAdmin):
```sql
CREATE DATABASE expense_tracker_db;
```

### Step 3: Run Migrations
Apply all pre-built Django migrations to create the schema:
```powershell
python manage.py migrate
```

### Step 4: Seed Demo Data (Optional but Recommended)
Populates demo user (`jordan`, password: `password123`), default categories with emoji icons, monthly budget, savings goals, and starter transactions matching the frontend:
```powershell
python manage.py seed_demo_data
```

### Step 5: Run Unit Tests
Verify all 10 automated test suites pass:
```powershell
python manage.py test
```

### Step 6: Start Development Server
```powershell
python manage.py runserver
```
The API is now running at `http://127.0.0.1:8000/`.

---

## 🔐 5. API Reference

All protected endpoints require the following HTTP header:
`Authorization: Bearer <access_token>`

### 🔑 Authentication (`/api/auth/`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user, auto-seeds default categories & budget, returns user + JWT tokens | No |
| `POST` | `/api/auth/login/` | Log in with username/email & password, returns user + JWT tokens | No |
| `POST` | `/api/auth/refresh/` | Obtain a new access token using a refresh token | No |
| `GET` | `/api/auth/me/` | Get current authenticated user profile & preferences | Yes |
| `PATCH` | `/api/auth/me/` | Update user profile (e.g., currency, theme) | Yes |
| `POST` | `/api/auth/reset-data/` | Resets all data (transactions, custom categories, budget, goals) | Yes |

#### Sample Register Request:
```json
POST /api/auth/register/
{
  "username": "alex",
  "email": "alex@example.com",
  "password": "securepassword123",
  "first_name": "Alex",
  "last_name": "Rivers",
  "currency": "$",
  "theme": "light"
}
```

#### Sample Register / Login Response:
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "username": "alex",
    "email": "alex@example.com",
    "first_name": "Alex",
    "last_name": "Rivers",
    "full_name": "Alex Rivers",
    "initials": "AR",
    "currency": "$",
    "theme": "light"
  },
  "tokens": {
    "refresh": "<jwt_refresh_token>",
    "access": "<jwt_access_token>"
  }
}
```

---

### 🏷️ Categories (`/api/categories/`)

| Method | Endpoint | Description | Query Parameters |
|---|---|---|---|
| `GET` | `/api/categories/` | List categories for user | `?type=expense`, `?type=income`, `?grouped=true` |
| `POST` | `/api/categories/` | Create a custom category | None |
| `GET` | `/api/categories/<id>/` | Retrieve category details | None |
| `PATCH` | `/api/categories/<id>/` | Update category (e.g. limit, icon, name) | None |
| `DELETE` | `/api/categories/<id>/` | Delete custom category (defaults protected) | None |

#### Sample Create Category Request:
```json
POST /api/categories/
{
  "name": "Fitness",
  "type": "expense",
  "icon": "🏋️",
  "limit": 120.00
}
```

---

### 💳 Transactions (`/api/transactions/`)

| Method | Endpoint | Description | Query Parameters |
|---|---|---|---|
| `GET` | `/api/transactions/` | List transactions | `?search=...`, `?type=...`, `?category=...`, `?sort=date\|amount`, `?month=YYYY-MM`, `?limit=5` |
| `POST` | `/api/transactions/` | Create a new transaction | None |
| `GET` | `/api/transactions/<id>/` | Retrieve transaction details | None |
| `PUT/PATCH` | `/api/transactions/<id>/` | Update a transaction | None |
| `DELETE` | `/api/transactions/<id>/` | Delete a transaction | None |
| `GET` | `/api/transactions/summary/`| Aggregate summary & monthly activity | None |
| `POST` | `/api/transactions/clear/` | Clear all user transactions | None |

#### Sample Create Transaction Request:
```json
POST /api/transactions/
{
  "name": "Whole Foods Market",
  "amount": 86.40,
  "type": "expense",
  "category": "Food",
  "date": "2024-06-08",
  "description": "Weekly groceries",
  "recurring": false,
  "repeat": "monthly"
}
```

#### Sample Summary Response (`GET /api/transactions/summary/`):
```json
{
  "balance": 4725.61,
  "income": 5750.00,
  "expenses": 1024.39,
  "savingsRate": 82,
  "monthExpenses": 213.39,
  "topCategory": ["Food", 86.40],
  "categoryTotals": {
    "Food": 86.40,
    "Transport": 72.00,
    "Bills": 54.99
  },
  "monthlyActivity": [
    { "month": "May", "key": "2024-05", "income": 4800.0, "expense": 1150.0 },
    { "month": "Jun", "key": "2024-06", "income": 5750.0, "expense": 213.39 }
  ]
}
```

---

### 🎯 Budgets & Savings Goals (`/api/budgets/`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/budgets/` | Get monthly budget, spent this month, percent used, and warning status |
| `PUT/PATCH`| `/api/budgets/` | Update monthly budget limit |
| `GET` | `/api/budgets/goals/` | List savings goals |
| `POST` | `/api/budgets/goals/` | Create savings goal |
| `PATCH` | `/api/budgets/goals/<id>/`| Update savings goal (e.g. saved amount) |
| `DELETE`| `/api/budgets/goals/<id>/`| Delete savings goal |

#### Sample Monthly Budget Response (`GET /api/budgets/`):
```json
{
  "amount": 2000.0,
  "spent_this_month": 213.39,
  "remaining": 1786.61,
  "percent_used": 11,
  "is_warning": false
}
```

#### Sample Savings Goal Request:
```json
POST /api/budgets/goals/
{
  "name": "Emergency Fund",
  "target": 5000.00,
  "saved": 1500.00
}
```

---

## ⚡ 6. Connecting to the Existing React Frontend

To connect the React frontend (`expense-tracker`) to this backend:

1. Create an API client in `expense-tracker/src/utils/api.js`:
```javascript
const API_BASE = "http://localhost:8000/api";

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem("expense_access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && localStorage.getItem("expense_refresh_token")) {
    // Refresh access token
    const refreshRes = await fetch(`${API_BASE}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: localStorage.getItem("expense_refresh_token") }),
    });
    if (refreshRes.ok) {
      const data = await refreshRes.json();
      localStorage.setItem("expense_access_token", data.access);
      headers.Authorization = `Bearer ${data.access}`;
      return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    }
  }

  return response;
}
```

2. Replace `localStorage` updates with API calls, e.g.:
- `GET /api/transactions/` replaces `localStorage.getItem("expense-transactions")`
- `POST /api/transactions/` on `addTransaction`
- `PATCH /api/transactions/:id/` on `updateTransaction`
- `DELETE /api/transactions/:id/` on `deleteTransaction`
- `GET /api/categories/` replaces hardcoded category lists
- `GET /api/budgets/` and `GET /api/budgets/goals/` replaces local budgets and goals.
