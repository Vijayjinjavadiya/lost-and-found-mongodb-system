# 🔍 Lost and Found Item Management System
### Subject: NoSQL (GTU) | Tech Stack: Python + MongoDB + Streamlit

---

## 📦 Project Structure

```
Nosql_project/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This setup guide
└── .streamlit/
    └── secrets.toml          # MongoDB connection URI (private)
```

---

## ⚙️ Step-by-Step Setup Guide

### Step 1 – Install Python
Download and install Python 3.10+ from https://www.python.org/downloads/
Make sure to check **"Add Python to PATH"** during installation.

---

### Step 2 – Install Required Libraries
Open Command Prompt or Terminal and run:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install streamlit pymongo pandas dnspython
```

---

### Step 3 – Setup MongoDB Atlas (Cloud)

1. Go to https://www.mongodb.com/atlas
2. Sign up for a **free account**
3. Create a **Free Cluster** (M0 tier — no credit card needed)
4. In the left menu → **Database Access** → Add a new user
   - Username: `admin`, Password: `yourpassword`
5. In the left menu → **Network Access** → Add IP Address → **Allow from Anywhere** (0.0.0.0/0)
6. Click **Connect** on your cluster → **Drivers** → Select **Python**
7. Copy the connection string (looks like):
   ```
   mongodb+srv://vijay_jinjavadiya_DB:<password>@nosqlproject.ud5qptz.mongodb.net/
   ```

---

### Step 4 – Configure Connection String

Open `.streamlit/secrets.toml` and paste your connection string:
```toml
MONGO_URI = "mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
```

> ⚠️ Replace `<password>` with your actual Atlas password.

---

### Step 5 – Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at: **http://localhost:8501**

---

## 🗄️ Database Structure

- **Database Name:** `lost_found_db`
- **Collection Name:** `items`

### Sample Document:
```json
{
    "_id": ObjectId("664c1a2b3f4e5d6a7b8c9d0e"),
    "title": "Blue Wallet",
    "description": "Navy blue leather wallet",
    "category": "Accessories",
    "location": "Central Library",
    "contact": "9876543210",
    "status": "Lost",
    "date": "2024-04-15 10:30"
}
```

---

## ✅ Features

| Feature | Description |
|---------|-------------|
| Add Item | Report a lost or found item with full details |
| View All Items | See all items in a styled table |
| Search & Filter | Filter by category, location, or keyword |
| Update Status | Change status from Lost → Found |
| Delete Item | Remove an item from the database |
| MongoDB Info | Learn MongoDB concepts and queries |

---

## 🔗 Useful Links
- MongoDB Atlas: https://www.mongodb.com/atlas
- Streamlit Docs: https://docs.streamlit.io
- PyMongo Docs: https://pymongo.readthedocs.io
