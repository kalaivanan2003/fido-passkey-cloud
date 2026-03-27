# 🔐 FIDO Cloud — Multi-Factor Authentication File Storage System

> A web-based multi-factor authentication (MFA) system combining **face recognition**, **FIDO key verification**, and **QR code scanning** with end-to-end encrypted cloud file storage.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the App](#running-the-app)
- [Authentication Flow](#authentication-flow)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Routes](#api-routes)
- [Security Notes](#security-notes)

---

## Overview

FIDO Cloud is a three-factor authentication system that allows users to securely register, get approved by an admin server and backup server, and then log in using:

1. **Password** — Traditional credential check
2. **Face Recognition** — Browser-based face verification using `face-api.js`
3. **FIDO Key + QR Code** — Cryptographic key verification via QR scan

All user files are encrypted using **ECIES (Elliptic Curve Integrated Encryption Scheme)** before being stored.

---

## ✨ Features

- 🧑 User registration with auto-generated EC key pairs
- 👤 Browser-based face capture and verification (no server webcam required)
- 🔑 FIDO key generation and XOR-based key splitting
- 📷 QR code generation and delivery via email
- 🗂️ Encrypted file upload, storage, and decryption
- 🛡️ Blockchain-style hash chaining for tamper detection
- 📧 Automated email alerts for suspicious login attempts
- 💾 SQLite database — no separate DB server required

---

## 🏗️ System Architecture

```
User Browser
    │
    ├──── Step 1: Register (password + face capture)
    ├──── Step 2: Admin Server approves → sends FIDO key via email
    ├──── Step 3: Backup Server approves → generates QR code
    │
    └──── Login Flow:
            Password ──► Face Scan ──► FIDO Key ──► QR Code Scan ──► Access
```

Three roles operate on the system:
| Role | URL | Credentials |
|---|---|---|
| **User** | `/UserLogin` | Registered username & password |
| **Admin Server** | `/ServerLogin` | `server` / `server` |
| **Backup Server** | `/BackupServer` | `server` / `server` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask |
| **Database** | SQLite (built-in, no server needed) |
| **Encryption** | ECIES (`eciespy`), SHA-256 HMAC |
| **Face Recognition** | `face-api.js` (browser-based) |
| **QR Code** | `qrcode` (Python), `jsQR` (browser) |
| **Email** | Gmail SMTP |
| **Deployment** | Gunicorn (Linux/Ubuntu) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd FIDOCloudPy

# 2. Create and activate a virtual environment
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialise the SQLite database (run ONCE)
python init_db.py
```

### Running the App

#### Development (Windows)
```bash
venv\Scripts\python.exe App.py
```

#### Development (Linux / macOS)
```bash
bash start.sh
# or
python App.py
```

#### Production (Linux with Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 App:app
```

Then open your browser at: **http://localhost:5000**

---

## 🔐 Authentication Flow

```
┌─────────────────────────────────────────────────────┐
│                   USER REGISTRATION                  │
│  Fill form ──► Auto-generate EC key pair             │
│  ──► Save to DB (status: Waiting)                    │
│  ──► Capture face via browser camera                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               ADMIN SERVER APPROVAL                  │
│  Review pending users ──► Approve                    │
│  ──► Generate prikey1, compute prikey2 (XOR split)   │
│  ──► Email FIDO key to user                          │
│  ──► Status: "Awaiting Backup Server"                │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              BACKUP SERVER APPROVAL                  │
│  Encrypt prikey1 with user's public key              │
│  ──► Generate QR code (contains prikey2)             │
│  ──► Email QR code to user                           │
│  ──► Status: "Approved"                              │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                    USER LOGIN                        │
│  1. Password check                                   │
│  2. Face verification (browser camera vs stored)     │
│  3. Enter FIDO key received by email                 │
│  4. Scan QR code received by email                   │
│  ──► Access Granted ✅                               │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
FIDOCloudPy/
├── App.py                  # Main Flask application
├── init_db.py              # One-time SQLite DB initialiser
├── requirements.txt        # Python dependencies
├── start.sh                # Linux startup script
├── start.bat               # Windows startup script
├── .gitignore
├── README.md
│
├── templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── NewUser.html
│   ├── UserLogin.html
│   ├── UserHome.html
│   ├── FaceCapture.html    # Browser face capture (face-api.js)
│   ├── FaceVerify.html     # Browser face verification
│   ├── FIDOVerify.html
│   ├── QrScan.html         # Browser QR scanner (jsQR)
│   ├── ServerLogin.html
│   ├── ServerHome.html
│   ├── BackupServer.html
│   ├── BackupServerHome.html
│   └── ...
│
├── static/
│   ├── upload/             # Original uploaded files
│   ├── Encrypt/            # Encrypted file storage
│   ├── Decrypt/            # Decrypted file downloads
│   └── Qrcode/             # Generated QR code images
│
└── fsdk/                   # Face SDK assets
```

---

## 🗃️ Database Schema

All data is stored in `fidoclouddb.sqlite` (auto-created by `init_db.py`).

### `regtb` — User Registrations
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| Name | TEXT | Full name |
| Mobile | TEXT | Phone number |
| Email | TEXT | Email address |
| Address | TEXT | Postal address |
| UserName | TEXT | Login username |
| Password | TEXT | Login password |
| Status | TEXT | `waiting` / `Awaiting Backup Server` / `Approved` |
| Pubkey | TEXT | EC public key (hex) |
| Prikey | TEXT | EC private key (hex) |
| prikey1 | TEXT | Server-generated key share |
| prikey2 | TEXT | XOR-derived key share (FIDO key) |
| face_encoding | TEXT | JSON face descriptor from face-api.js |

### `backuptb` — Backup Server Records
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| UserName | TEXT | Linked username |
| Enckey | TEXT | Encrypted prikey1 (hex) |
| pubkey | TEXT | User's public key |
| prikey2 | TEXT | FIDO key share |
| Qrcode | TEXT | QR image filename |
| Hash1 | TEXT | Previous block hash (chain) |
| Hash2 | TEXT | Current block hash |

### `filetb` — File Storage
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| OwnerName | TEXT | Uploader username |
| FileInfo | TEXT | File description |
| FileName | TEXT | Stored filename |
| Pukey | TEXT | File encryption public key |
| Pvkey | TEXT | File decryption private key |
| hash1 | TEXT | Previous block hash |
| hash2 | TEXT | Current block hash |

### `temptb` — Temporary Face Auth Sessions
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| UserName | TEXT | Verified username (cleared after login) |

---

## 🌐 API Routes

| Method | Route | Description |
|---|---|---|
| GET | `/` | Home page |
| GET/POST | `/newuser` | User registration |
| GET | `/face-capture` | Face capture page |
| POST | `/save-face` | Save face encoding |
| GET/POST | `/userlogin` | User login (password) |
| GET | `/face-verify` | Face verification page |
| POST | `/verify-face` | Verify face encoding |
| GET/POST | `/vlogin` | FIDO key verification |
| GET | `/qr-scan` | QR code scan page |
| POST | `/verify-qr` | Verify QR code |
| GET | `/UserHome` | User dashboard |
| GET | `/UserFileUpload` | File upload page |
| POST | `/usfileupload` | Upload & encrypt file |
| GET | `/UserFileInfo` | View user's files |
| POST | `/search` | Search files |
| GET | `/Decryptkey` | Request file decrypt key |
| POST | `/fdecrypt` | Decrypt and download file |
| GET/POST | `/serverlogin` | Admin server login |
| GET | `/ServerHome` | Admin dashboard |
| GET | `/Approved` | Approve user registration |
| GET | `/Reject` | Reject user registration |
| GET/POST | `/bslogin` | Backup server login |
| GET | `/BackupServerHome` | Backup server dashboard |
| GET | `/QrApproved` | Generate & send QR code |
| GET | `/SFileInfo` | View all files (server) |
| GET | `/QrcodeInfo` | View all QR records |

---

## 🔒 Security Notes

- All file content is encrypted with **ECIES** (Elliptic Curve Integrated Encryption Scheme) before disk storage.
- The private key is **split using XOR** between the main server and backup server — neither alone can reconstruct it.
- Files are chained with **SHA-256 HMAC hashes** for tamper detection.
- Unauthorized login attempts send an **email alert with a captured photo** of the intruder.
- All database queries use **parameterized statements** to prevent SQL injection.

> ⚠️ For production deployment, replace the hardcoded email credentials and `SECRET_KEY` in `App.py` with environment variables.

---

## 📄 License

This project is for academic/research purposes.
