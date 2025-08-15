# FastAPI + OpenSearch

A lightweight FastAPI application integrated with OpenSearch for efficient data indexing and searching.
It returns the data from local db, and if local db doesn't contain the data then it fetches from external db and save to local db and return the data.

---

## 📦 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.10+**
- **OpenSearch** (v2.x or higher recommended)
- **pip** (Python package installer)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/samyog777/FastAPI-OpenSearch.git
cd FastAPI-OpenSearch
```

### 2. Configure Environment Variables
Copy `.env_example` to `.env` in the project root:
```bash
cp .env_example .env
```

**Example `.env_example`:**
```env
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_INDEX=items
```

Update the values to match your OpenSearch configuration.

---

### 3. Create a Python Virtual Environment
```bash
python -m venv .venv
```

**Activate the environment:**
- **Windows (PowerShell):**
```bash
.venv\Scripts\Activate
```
- **Linux/Mac:**
```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 5. Set Up OpenSearch
1. **Install and Start OpenSearch**  
   [OpenSearch Installation Guide](https://opensearch.org/docs/latest/install-and-configure/)

2. **Create the Index** (matching your `.env` configuration):
```bash
curl -X PUT "localhost:9200/items" -u admin:admin
```

---

## 🚀 Run the Application
```bash
python run.py
```

The application will run at:
```
http://127.0.0.1:8000
```

---

## 📂 Project Structure
```
.
├── app
│   ├── external
│   │   ├── __init__.py
│   │   └── university_data.py
│   ├── __init__.py
│   ├── main.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── universities.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── item.py
│   │   └── university.py
│   └── services
│       ├── base_opensearch.py
│       ├── __init__.py
│       ├── items.py
│       └── university.py
├── readme.md          # 
├── .env_example       # Environment variables template
├── requirements.txt   # Python dependencies
└── run.py             # Application entry point
```

---