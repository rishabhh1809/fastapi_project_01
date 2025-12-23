**AI GENERATED README FILE**

# 🎫 Event Ticketing Platform

A high-performance, production-ready **Event Ticketing Platform API** built with FastAPI, featuring asynchronous database operations, JWT authentication, role-based access control, and Prometheus metrics.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Database Schema](#database-schema)
- [Development](#development)
- [Monitoring](#monitoring)

---

## 🎯 Overview

The Event Ticketing Platform is a RESTful API service designed to manage events and ticket bookings. It provides a complete backend solution for:

- **Event Management**: Create, update, delete, and list events with seat capacity tracking
- **Booking System**: Handle ticket reservations with concurrency-safe seat allocation
- **User Authentication**: JWT-based authentication with role-based access control
- **High Performance**: Async operations with connection pooling and uvloop optimization

---

## ✨ Features

| Feature                   | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| 🚀 **Async Support**      | Full async/await support using SQLAlchemy 2.0 and asyncpg |
| 🔐 **JWT Authentication** | Secure authentication with access and refresh tokens      |
| 👥 **Role-Based Access**  | Admin and user roles with granular permissions            |
| 📊 **Prometheus Metrics** | Built-in metrics endpoint for monitoring                  |
| 🔄 **CORS Support**       | Configurable Cross-Origin Resource Sharing                |
| 🐘 **PostgreSQL**         | Production-grade database with connection pooling         |
| ⚡ **uvloop**             | High-performance event loop for better throughput         |
| 🔒 **Concurrency Safety** | Row-level locking for booking operations                  |
| 📝 **OpenAPI Docs**       | Auto-generated Swagger and ReDoc documentation            |
| 🏗️ **Modular Design**     | Clean separation of concerns with layered architecture    |

---

## 🏛️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                       │
│                    (Web, Mobile, Third-party)                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Server                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │    CORS     │  │   Auth      │  │   Exception Handlers    │ │
│  │ Middleware  │  │ Middleware  │  │   (Global/Validation)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Versioning                            │
│                         /api/v1/*                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Event Manager        │     │    Booking Manager      │
│  /api/v1/events/*       │     │  /api/v1/bookings/*     │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Service Layer                            │
│              (Business Logic & Validation)                       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Access Layer (DAO)                     │
│              (Database Operations & Queries)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                            │
│                  (Async with asyncpg)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Layered Architecture Pattern

The application follows a **clean layered architecture**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Routers    │  Controllers  │  Request/Response Schemas    ││
│  │  (routes)   │  (handlers)   │  (validation)                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BUSINESS LAYER                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Services         │  Business Rules  │  Validations        ││
│  │  (EventService)   │  (seat logic)    │  (constraints)      ││
│  │  (BookingService) │  (booking rules) │                     ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA ACCESS LAYER                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  DAO Classes     │  ORM Models      │  Database Utilities  ││
│  │  (EventDAO)      │  (Event)         │  (CRUD operations)   ││
│  │  (BookingDAO)    │  (Booking)       │  (transactions)      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
fastapi_project_01/
├── requirements.txt          # Python dependencies
├── start.sh                  # Startup script (Docker + FastAPI)
├── README.md                 # Project documentation
│
└── src/
    ├── app/                  # Core application module
    │   ├── __init__.py
    │   ├── main.py           # FastAPI application entry point
    │   ├── auth.py           # JWT authentication & authorization
    │   ├── database.py       # Database configuration & utilities
    │   ├── routers.py        # Main router aggregation
    │   ├── settings.py       # Configuration management (Pydantic)
    │   ├── utility.py        # Helper functions & response classes
    │   └── project_schemas.py # Global Pydantic schemas
    │
    └── modules/              # Feature modules
        └── V1/               # API Version 1
            ├── v1routers.py  # V1 route aggregation
            │
            ├── eventmanager/ # Event management module
            │   ├── models.py     # SQLAlchemy Event model
            │   ├── schemas.py    # Pydantic validation schemas
            │   ├── dao.py        # Data Access Object
            │   ├── services.py   # Business logic
            │   ├── controller.py # Request handling
            │   ├── routers.py    # Route definitions
            │   └── api_docs.py   # OpenAPI documentation
            │
            └── bookingmanager/ # Booking management module
                ├── models.py     # SQLAlchemy Booking model
                ├── schemas.py    # Pydantic validation schemas
                ├── dao.py        # Data Access Object
                ├── services.py   # Business logic
                ├── controller.py # Request handling
                ├── routers.py    # Route definitions
                └── api_docs.py   # OpenAPI documentation
```

### Module Components Explained

| Component         | Purpose                                              |
| ----------------- | ---------------------------------------------------- |
| **models.py**     | SQLAlchemy ORM model definitions with table mappings |
| **schemas.py**    | Pydantic models for request/response validation      |
| **dao.py**        | Data Access Object - database query operations       |
| **services.py**   | Business logic layer with validation rules           |
| **controller.py** | HTTP request handling and response formatting        |
| **routers.py**    | FastAPI route definitions with dependencies          |
| **api_docs.py**   | OpenAPI documentation strings                        |

---

## 🛠️ Technology Stack

### Core Framework

- **[FastAPI](https://fastapi.tiangolo.com/)** (v0.127.0) - Modern, high-performance web framework
- **[Uvicorn](https://www.uvicorn.org/)** (v0.40.0) - ASGI server with uvloop
- **[uvloop](https://github.com/MagicStack/uvloop)** (v0.22.1) - Ultra-fast event loop

### Database

- **[PostgreSQL](https://www.postgresql.org/)** (v17) - Primary database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** (v2.0.45) - ORM with async support
- **[asyncpg](https://github.com/MagicStack/asyncpg)** (v0.31.0) - Async PostgreSQL driver

### Authentication & Security

- **[PyJWT](https://pyjwt.readthedocs.io/)** (v2.10.1) - JSON Web Token implementation
- **[passlib](https://passlib.readthedocs.io/)** + **bcrypt** (v5.0.0) - Password hashing
- **[python-jose](https://python-jose.readthedocs.io/)** (v3.5.0) - JOSE implementation

### Configuration & Validation

- **[Pydantic](https://pydantic-docs.helpmanual.io/)** (v2.12.5) - Data validation
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** (v2.12.0) - Settings management
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** (v1.2.1) - Environment variables

### Monitoring & Serialization

- **[Prometheus FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)** (v7.1.0) - Metrics
- **[orjson](https://github.com/ijl/orjson)** (v3.11.5) - Fast JSON serialization

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+
- **Docker** (for PostgreSQL)
- **Git**

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/rishabhh1809/fastapi_project_01.git
   cd fastapi_project_01
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # OR
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start with the startup script (recommended)**

   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   This script will:

   - ✅ Check and start Docker
   - ✅ Create/start PostgreSQL container
   - ✅ Wait for database readiness
   - ✅ Activate virtual environment
   - ✅ Start FastAPI with hot-reload

5. **Access the API**
   - 📍 **API Base**: http://localhost:8000
   - 📚 **Swagger Docs**: http://localhost:8000/docs
   - 📖 **ReDoc**: http://localhost:8000/redoc
   - 📊 **Metrics**: http://localhost:8000/metrics

### Manual Setup

If you prefer manual setup:

```bash
# Start PostgreSQL
docker run -d \
  --name postgres-ticketing \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=event_ticketing \
  -p 5432:5432 \
  postgres:17-alpine

# Run the application
cd src
uvicorn app.main:app --host localhost --port 8000 --reload
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `src/` directory:

```env
# Application
PROJECT_NAME=Event Ticketing Platform
PROJECT_DOMAIN=localhost
DEBUG=true

# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=event_ticketing
DB_ECHO=false
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Security
JWT_SECRET=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

### Settings Classes

| Setting Class      | Purpose                               |
| ------------------ | ------------------------------------- |
| `AppSettings`      | Application name, version, debug mode |
| `DatabaseSettings` | PostgreSQL connection and pooling     |
| `SecuritySettings` | JWT configuration                     |
| `CORSSettings`     | Cross-origin settings                 |
| `RedisSettings`    | Redis cache configuration             |

---

## 📖 API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Events API

| Method   | Endpoint             | Description           | Auth     |
| -------- | -------------------- | --------------------- | -------- |
| `GET`    | `/events`            | List all events       | ❌       |
| `POST`   | `/events`            | Create a new event    | 🔐 Admin |
| `GET`    | `/events/available`  | List available events | ❌       |
| `GET`    | `/events/{event_id}` | Get event details     | ❌       |
| `PUT`    | `/events/{event_id}` | Update event          | 🔐 Admin |
| `PATCH`  | `/events/{event_id}` | Partial update        | 🔐 Admin |
| `DELETE` | `/events/{event_id}` | Delete event          | 🔐 Admin |

### Bookings API

| Method   | Endpoint                     | Description         | Auth     |
| -------- | ---------------------------- | ------------------- | -------- |
| `GET`    | `/bookings`                  | Get user's bookings | 🔐 User  |
| `POST`   | `/bookings`                  | Create a booking    | 🔐 User  |
| `GET`    | `/bookings/{booking_id}`     | Get booking details | 🔐 User  |
| `DELETE` | `/bookings/{booking_id}`     | Cancel booking      | 🔐 User  |
| `GET`    | `/bookings/all`              | Get all bookings    | 🔐 Admin |
| `GET`    | `/bookings/event/{event_id}` | Get event bookings  | 🔐 Admin |

### Response Format

All API responses follow a consistent structure:

```json
{
  "code": 200,
  "message": "Success",
  "status": "success",
  "data": { ... }
}
```

### Pagination

List endpoints support pagination:

```
GET /api/v1/events?skip=0&limit=100
```

---

## 🔐 Authentication

### JWT Token Flow

```
┌─────────┐                                           ┌─────────┐
│  Client │                                           │  Server │
└────┬────┘                                           └────┬────┘
     │                                                     │
     │  1. Login with credentials                          │
     │ ─────────────────────────────────────────────────► │
     │                                                     │
     │  2. Return access_token + refresh_token             │
     │ ◄───────────────────────────────────────────────── │
     │                                                     │
     │  3. Request with Authorization: Bearer <token>      │
     │ ─────────────────────────────────────────────────► │
     │                                                     │
     │  4. Validate token & return data                    │
     │ ◄───────────────────────────────────────────────── │
     │                                                     │
```

### Token Types

| Token             | Expiry     | Purpose                  |
| ----------------- | ---------- | ------------------------ |
| **Access Token**  | 30 minutes | API authentication       |
| **Refresh Token** | 7 days     | Obtain new access tokens |

### Authorization Header

```http
Authorization: Bearer eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9...
```

### Role-Based Access Control

| Role      | Permissions                            |
| --------- | -------------------------------------- |
| **user**  | View events, manage own bookings       |
| **admin** | Full access to events and all bookings |

---

## 🗄️ Database Schema

### Events Table

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    venue VARCHAR(255),
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Bookings Table

```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Booking Status Enum

| Status      | Description       |
| ----------- | ----------------- |
| `pending`   | Booking initiated |
| `confirmed` | Booking confirmed |
| `cancelled` | Booking cancelled |
| `expired`   | Booking expired   |

### Entity Relationship Diagram

```
┌─────────────────────────────────────────┐
│                EVENTS                    │
├─────────────────────────────────────────┤
│ id (PK)         │ SERIAL                │
│ title           │ VARCHAR(255)          │
│ description     │ VARCHAR(1000)         │
│ date            │ TIMESTAMP             │
│ venue           │ VARCHAR(255)          │
│ total_seats     │ INTEGER               │
│ available_seats │ INTEGER               │
│ price           │ NUMERIC(10,2)         │
│ created_at      │ TIMESTAMP             │
│ updated_at      │ TIMESTAMP             │
└────────────────────┬────────────────────┘
                     │
                     │ 1:N
                     │
┌────────────────────┴────────────────────┐
│               BOOKINGS                   │
├─────────────────────────────────────────┤
│ id (PK)         │ SERIAL                │
│ event_id (FK)   │ INTEGER               │
│ user_id         │ VARCHAR(255)          │
│ quantity        │ INTEGER               │
│ status          │ ENUM                  │
│ created_at      │ TIMESTAMP             │
│ updated_at      │ TIMESTAMP             │
└─────────────────────────────────────────┘
```

---

## 💻 Development

### Code Style

The project follows Python best practices:

- Type hints throughout the codebase
- Async/await for all I/O operations
- Pydantic models for data validation
- Separation of concerns (Router → Controller → Service → DAO)

### Adding a New Module

1. Create module directory under `src/modules/V1/`
2. Add the following files:

   - `models.py` - SQLAlchemy model
   - `schemas.py` - Pydantic schemas
   - `dao.py` - Data access operations
   - `services.py` - Business logic
   - `controller.py` - Request handlers
   - `routers.py` - Route definitions
   - `api_docs.py` - Documentation

3. Register routes in `src/modules/V1/v1routers.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

---

## 📊 Monitoring

### Prometheus Metrics

Access metrics at: `http://localhost:8000/metrics`

Available metrics include:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Current active requests

### Health Check

```bash
curl http://localhost:8000/
```

Response:

```json
{
	"code": 200,
	"message": "Success",
	"status": "success",
	"data": {
		"name": "Event Ticketing Platform",
		"version": "1.0.0",
		"status": "healthy"
	}
}
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Rishabh** - [GitHub](https://github.com/rishabhh1809)

---

## 🙏 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
