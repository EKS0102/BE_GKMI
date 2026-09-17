# BE-GKMI

Backend API untuk sistem **Presensi Jemaat**.

Project ini dibangun menggunakan FastAPI dengan arsitektur berlapis yang memisahkan HTTP layer, service, transaction management, repository, dan database.

## Overview

BE-GKMI menyediakan REST API untuk:

* Authentication dan authorization
* User registration dan login
* JWT access token dan refresh token
* Pengelolaan data Jemaat
* Bulk creation data Jemaat
* Role-Based Access Control (RBAC)
* Audit log
* Login attempt tracking
* Refresh token management
* Database migration menggunakan Alembic
* Health check dan database readiness check

## Tech Stack

* Python 3.14
* FastAPI
* SQLAlchemy
* PostgreSQL 15
* Psycopg 3
* Alembic
* Pydantic
* PyJWT
* Argon2
* Uvicorn
* Pytest
* Coverage
* Docker / Docker Compose

## Architecture

Request diproses melalui alur:

```text
Router
   ↓
FastAPI Depends
   ↓
Service
   ↓
UnitOfWork
   ↓
Repository
   ↓
SQLAlchemy Session
   ↓
PostgreSQL
```

### Layer Responsibilities

**Router**

* Menangani HTTP request/response
* Validasi input melalui schema
* Dependency injection
* Authorization dependency

**Service**

* Business logic
* Transaction flow
* Validasi aturan bisnis

**UnitOfWork**

* Mengelola satu SQLAlchemy session
* Menyediakan repository
* Commit / rollback transaction

**Repository**

* Menangani operasi database
* Tidak membuat session sendiri
* Tidak melakukan commit/rollback sendiri

**Database**

* PostgreSQL

## Project Structure

```text
BE-GKMI/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── auth/
│   ├── auth.py
│   ├── refresh_token.py
│   └── security.py
│
├── database/
│   └── database.py
│
├── models/
│   ├── audit_log.py
│   ├── jemaat.py
│   ├── login_attempt.py
│   ├── refresh_token.py
│   └── user.py
│
├── repositories/
│   ├── audit_log_repository.py
│   ├── jemaat_repository.py
│   ├── login_attempt_repository.py
│   ├── refresh_token_repository.py
│   └── user_repository.py
│
├── routers/
│   ├── auth.py
│   └── jemaat.py
│
├── schemas/
│   ├── jemaat.py
│   └── user.py
│
├── services/
│   ├── auth_service.py
│   ├── jemaat_service.py
│   └── security_cleanup_service.py
│
├── tests/
│   ├── unit/
│   └── *.py
│
├── config.py
├── dependencies.py
├── docker-compose.yml
├── Dockerfile
├── logger.py
├── main.py
├── requirements.txt
└── unit_of_work.py
```

## Requirements

Untuk menjalankan project secara lokal:

* Python 3.14
* PostgreSQL 15
* Git

Untuk menjalankan menggunakan Docker:

* Docker Desktop
* Docker Compose

## Environment Variables

Buat file `.env` berdasarkan `.env.example`.

Contoh:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD
POSTGRES_DB=presensi_jemaat

TEST_DATABASE_NAME=presensi_jemaat_test

DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5433/presensi_jemaat

TEST_DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5433/presensi_jemaat_test

SECRET_KEY=YOUR_SECRET_KEY

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

ENVIRONMENT=development

LOG_DIR=logs
LOG_LEVEL=INFO
```

### Security

Jangan commit `.env`.

`.env` harus tetap berada di `.gitignore`.

Untuk production:

* Gunakan `SECRET_KEY` yang kuat dan unik.
* Jangan menggunakan placeholder seperti `YOUR_SECRET_KEY`.
* `SECRET_KEY` production harus memiliki panjang minimal 32 karakter.
* `CORS_ORIGINS` wajib dikonfigurasi.
* Jangan menggunakan credential development untuk production.

## Local Development

### 1. Clone repository

```bash
git clone https://github.com/EKS0102/BE_GKMI.git
cd BE-GKMI
```

### 2. Create virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Aktifkan:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment

Buat `.env` berdasarkan `.env.example`.

Pastikan PostgreSQL tersedia dan database sudah sesuai dengan konfigurasi.

### 5. Run migration

```powershell
alembic upgrade head
```

### 6. Run API

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

API tersedia pada:

```text
http://localhost:8000
```

## Docker

Docker Compose menyediakan:

* PostgreSQL 15
* FastAPI API
* PostgreSQL persistent volume
* API healthcheck
* PostgreSQL healthcheck

### Build

```powershell
docker compose build
```

### Start

```powershell
docker compose up -d
```

### Check container

```powershell
docker compose ps
```

### API health

```powershell
Invoke-WebRequest http://localhost:8000/health -UseBasicParsing
```

Expected:

```json
{"status":"ok"}
```

### Database readiness

```powershell
Invoke-WebRequest http://localhost:8000/health/ready -UseBasicParsing
```

Expected:

```json
{"status":"ready"}
```

### Stop

```powershell
docker compose down
```

> Jangan menggunakan `docker compose down -v` kecuali memang diperlukan untuk menghapus persistent database volume.

## Database & Alembic

Melihat migration head:

```powershell
alembic heads
```

Melihat migration database saat ini:

```powershell
alembic current
```

Menjalankan migration:

```powershell
alembic upgrade head
```

Rollback satu migration:

```powershell
alembic downgrade -1
```

Migration head saat review:

```text
73d3e9a981aa
```

## API

### Health

```text
GET /
GET /health
GET /health/ready
```

### Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

### Jemaat

```text
GET    /jemaat
GET    /jemaat/{jemaat_id}
POST   /jemaat
POST   /jemaat/bulk
PUT    /jemaat/{jemaat_id}
DELETE /jemaat/{jemaat_id}
```

Dokumentasi API tersedia melalui OpenAPI/FastAPI:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

## Authentication

Authentication menggunakan JWT.

Access token digunakan untuk endpoint yang membutuhkan authentication.

Header:

```text
Authorization: Bearer <access_token>
```

JWT menggunakan konfigurasi:

```text
ALGORITHM
SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
```

Refresh token dikelola menggunakan token hash dan memiliki mekanisme:

* expiration
* revocation
* active token lookup
* token cleanup

## Role-Based Access Control

Terdapat tiga role:

```text
admin
staff
viewer
```

Hak akses yang telah diverifikasi:

| Operation             | Viewer | Staff | Admin |
| --------------------- | -----: | ----: | ----: |
| GET `/jemaat`         |    200 |   200 |   200 |
| POST `/jemaat`        |    403 |   201 |   201 |
| PUT `/jemaat/{id}`    |    403 |   200 |   200 |
| DELETE `/jemaat/{id}` |    403 |   403 |   204 |

Secara umum:

* **Viewer**: read-only
* **Staff**: read dan create/update
* **Admin**: read, create, update, delete

Endpoint yang membutuhkan authentication akan mengembalikan `401` apabila tidak memiliki credential/token yang valid.

Endpoint yang tidak memiliki permission yang cukup akan mengembalikan `403`.

## Error Handling

API menggunakan standard HTTP status code untuk error.

Contoh:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
```

Global exception handler digunakan untuk menangani unexpected internal error.

Response internal error:

```json
{
  "message": "Internal Server Error"
}
```

Detail exception internal tidak dikirimkan kepada client.

## Logging

Log aplikasi disimpan pada:

```text
logs/app.log
```

Logging juga dikirimkan ke console.

Konfigurasi:

```env
LOG_DIR=logs
LOG_LEVEL=INFO
```

Secret, password, token, dan `SECRET_KEY` tidak boleh ditulis ke log.

## Security

Security controls yang telah diverifikasi:

* JWT authentication
* Role-Based Access Control
* Password hashing
* Refresh token expiration
* Refresh token revocation
* Login attempt tracking
* Security headers
* CORS restriction
* Global exception handling
* Production secret validation
* Production CORS validation
* Docker API berjalan sebagai non-root user
* Dependency vulnerability audit

Security headers yang digunakan:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Dependency audit terakhir:

```text
pip-audit
No known vulnerabilities found
```

## Testing

Menjalankan seluruh test:

```powershell
pytest -q
```

Menjalankan test dengan coverage:

```powershell
pytest --cov=. --cov-report=term-missing -q
```

Hasil final review:

```text
177 passed
2683 statements
60 missed
98% coverage
```

Production code utama mencapai 100% coverage.

Coverage yang belum 100% terutama berasal dari Alembic migration files dan utility `create_password.py`.

## Production Configuration

Production harus menggunakan:

```env
ENVIRONMENT=production
```

Production configuration melakukan validasi terhadap:

* Environment value
* Secret key
* CORS origins
* Required database configuration

Invalid environment akan ditolak.

Secret key yang terlalu pendek atau menggunakan placeholder development akan ditolak.

CORS tanpa konfigurasi pada production akan ditolak.

## Deployment Checklist

Sebelum deployment production:

* [ ] Set `ENVIRONMENT=production`
* [ ] Gunakan `SECRET_KEY` kuat dan unik
* [ ] Set `DATABASE_URL` production
* [ ] Set `TEST_DATABASE_URL` sesuai kebutuhan deployment/test environment
* [ ] Set `CORS_ORIGINS` ke origin frontend yang benar
* [ ] Pastikan PostgreSQL tersedia
* [ ] Jalankan `alembic upgrade head`
* [ ] Pastikan API healthcheck `200`
* [ ] Pastikan database readiness `200`
* [ ] Pastikan Docker API berjalan sebagai non-root
* [ ] Jalankan test suite
* [ ] Jalankan dependency audit
* [ ] Pastikan `.env` tidak masuk Git
* [ ] Review log untuk memastikan tidak ada secret/token/password
* [ ] Review security findings sebelum production release

## Known Security Finding

### Public Registration Privilege Assignment

Endpoint:

```text
POST /auth/register
```

saat ini memungkinkan client menentukan role pada saat registration.

Karena endpoint registration bersifat public, client dapat meminta role privileged seperti:

```text
admin
staff
```

Hal ini perlu diperbaiki sebelum production deployment jika registration memang dimaksudkan sebagai public self-registration.

Rekomendasi desain perlu ditentukan terlebih dahulu, misalnya:

* public registration selalu membuat `viewer`;
* role privileged hanya dapat diberikan oleh admin;
* atau registration privileged dipindahkan ke mekanisme internal/admin-only.

**Status: OPEN — perlu remediation sebelum production deployment.**

## Current Verification Status

Pada Production Readiness Review:

```text
Environment & .env Security       PASS
Docker & Docker Compose            PASS
Database & Alembic                 PASS
API Endpoint Verification          PASS
Authentication & Authorization     FINDING
Error Handling & Logging           PASS
CORS & Security Headers            PASS
Dependency Security                PASS
Production Configuration           PASS
Full Test & Coverage               PASS
```

Current Git branch:

```text
main
```

Latest verified checkpoint:

```text
2d5dba7 security: run api container as non-root
```

Repository harus tetap clean sebelum deployment atau perubahan berikutnya.
