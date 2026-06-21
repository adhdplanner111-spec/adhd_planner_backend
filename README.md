# ADHD Planner Backend & Admin Dashboard

Backend API dan Admin Dashboard untuk aplikasi **Smart ADHD Daily Planner**.

---

## Tech Stack

### Backend

* FastAPI
* Firebase Authentication
* Firestore Database
* JWT Authentication
* SMTP Email OTP
* Fernet Encryption

### Admin Dashboard

* React
* Vite
* Material UI
* Axios
* Recharts

---

# Clone Repository

```bash
git clone https://github.com/USERNAME/adhd_planner_backend.git

cd adhd_planner_backend
```

---

# Backend Installation

Buat virtual environment:

```bash
python -m venv venv
```

Aktifkan:

### Windows

```bash
venv\Scripts\activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Buat file:

```text
.env
```

Contoh:

```env
JWT_SECRET_KEY=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=

FIREBASE_WEB_API_KEY=

EMAIL_HOST=
EMAIL_PORT=

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

OTP_EXPIRE_MINUTES=

FERNET_KEY=

ADMIN_USERNAME=
ADMIN_PASSWORD=
```

---

# Firebase

Tambahkan:

```text
serviceAccountKey.json
```

ke root project:

```text
adhd_planner_backend/
│
├── serviceAccountKey.json
├── .env
└── app/
```

---

# Run Backend

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Admin Dashboard Installation

Masuk ke folder:

```bash
cd admin
```

Install dependency:

```bash
npm install
```

Jalankan:

```bash
npm run dev
```

Dashboard:

```text
http://localhost:5173
```

---

# Project Structure

```text
adhd_planner_backend/
│
├── app/
│   ├── core/
│   ├── routes/
│   ├── schemas/
│   └── utils/
│
├── admin/
│   ├── src/
│   └── package.json
│
├── .env
├── requirements.txt
├── serviceAccountKey.json
└── README.md
```

---

# Important Files

Jangan upload:

```text
.env
serviceAccountKey.json
venv/
admin/node_modules/
__pycache__/
```

---

# Generate requirements.txt

```bash
pip freeze > requirements.txt
```

---

# Install Admin Dependencies

```bash
cd admin

npm install
```

---

# Team Setup

1. Clone repository.
2. Tambahkan `.env`.
3. Tambahkan `serviceAccountKey.json`.
4. Install Python requirements.
5. Install admin dependencies.
6. Jalankan backend.
7. Jalankan admin dashboard.

---

# API Documentation

```text
http://127.0.0.1:8000/docs
```

---

# Authors

* Utbah Abdurrahman
* Hilman Bintang Ardhani