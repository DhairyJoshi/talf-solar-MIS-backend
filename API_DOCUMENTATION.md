# Talf Solar MIS Backend: API Documentation

This document provides a comprehensive technical reference for all API endpoints in the Talf Solar Management Information System.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Docs**: `http://localhost:8000/docs`

---

## 1. Authentication (`/auth`)

The system uses **OAuth2 with Password Grant (JWT Tokens)**.

### **POST** `/auth/register`
Creates a new user.
- **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "securepassword",
      "full_name": "John Doe",
      "role": "VIEWER" // ADMIN, OPERATIONS, VIEWER
    }
    ```

### **POST** `/auth/login`
Authenticates a user and returns a JWT.
- **Content-Type**: `application/x-www-form-urlencoded`
- **Body**: `username` (email), `password`
- **Response**: `{"access_token": "...", "token_type": "bearer"}`

### **GET** `/auth/me`
Retrieves the currently authenticated user profile.
- **Header**: `Authorization: Bearer <token>`

---

## 2. Projects (`/projects`)

### **GET** `/projects/`
Lists all solar projects in the portfolio.
- **Response**: Includes `inverters`, `monthly_data`, and `monthly_kpis` for dashboard aggregation.

### **POST** `/projects/`
Creates a new project.
- **Access**: `ADMIN`
- **Body**: `{"name": "...", "location": "...", "capacity_kw": 500.0}`

### **GET** `/projects/{id}`
Fetches a single project with full relationship data.

### **PUT** `/projects/{id}`
Updates project metadata.
- **Access**: `ADMIN`

### **DELETE** `/projects/{id}`
Removes a project and all associated inverters/data.
- **Access**: `ADMIN`

---

## 3. Inverters (`/inverters` & `/projects/{id}/inverters`)

### **GET** `/inverters/{id}`
Fetches inverter details. **Includes auto-prolonged `live_data`** (Power/Status) fetched from the vendor API.

### **POST** `/projects/{id}/inverters`
Adds an inverter to a specific project.
- **Access**: `ADMIN`
- **Body**:
    ```json
    {
      "serial_number": "SN12345",
      "vendor_type": "SOLISCLOUD", // SOLISCLOUD, SUNGROW, TRACKSO
      "api_key": "...",
      "api_secret": "...",
      "module_build_id": null
    }
    ```

### **PUT** `/inverters/{id}`
Updates inverter settings or links a `module_build_id`.
- **Access**: `ADMIN`

### **DELETE** `/inverters/{id}`
Deletes an inverter.
- **Access**: `ADMIN`

---

## 4. Real-time Inverter Proxy (`/proxy`)

Used for dynamic live dashboard widgets. Bypasses CORS and hides credentials.

### **GET** `/proxy/inverters/{id}/live-status`
Real-time power and online/offline status.
- **Response**: `{"vendor": "...", "power_output_kw": 12.5, "status": "ONLINE"}`

### **GET** `/proxy/inverters/{id}/day-curve`
Time-series power data for a specific date.
- **Params**: `date` (YYYY-MM-DD)
- **Response**: `{"data_points": [{"timestamp": "...", "value": ...}]}`

---

## 5. Monthly Yield Data (`/projects/{id}/monthly-data`)

### **POST** `/projects/{id}/monthly-data`
Add a single manual entry.
- **Access**: `ADMIN` or `OPERATIONS`
- **Body**: `{"month": "2024-03", "energy_kwh": 1250.0}`

### **POST** `/projects/{id}/monthly-data/csv`
Bulk upload energy data from a CSV file.
- **Access**: `ADMIN` or `OPERATIONS`
- **Format**: `multipart/form-data` with `file` field.
- **CSV Headers**: `month` (YYYY-MM), `energy_kwh`.

---

## 6. Performance KPIs (`/projects/{id}/kpis`)

### **GET** `/projects/{id}/kpis`
Lists pre-aggregated PR (Performance Ratio), CUF (Capacity Utilisation Factor), and P50 targets per month.

### **POST** `/projects/{id}/kpis/recalculate`
Trigger backend re-computation of all KPIs for a project.
- **Access**: `ADMIN` or `OPERATIONS`

---

## 7. Breakdown Events (`/inverters/{id}/breakdown-events`)

### **POST** `/inverters/{id}/breakdown-events`
Log a maintenance or breakdown event.
- **Access**: `ADMIN` or `OPERATIONS`
- **Body**: `{"event_type": "FAULT", "description": "...", "start_time": "...", "end_time": "..."}`

### **GET** `/inverters/{id}/breakdown-events`
View all logs for an inverter.

---

## 8. Role-Based Access Control (RBAC)

| Feature | ADMIN | OPERATIONS | VIEWER |
|---|---|---|---|
| User & System Mgmt | Yes | No | No |
| Project/Inverter Config | Yes | No | No |
| Manual Data Ingestion | Yes | Yes | No |
| KPI Recalculation | Yes | Yes | No |
| Real-time Monitoring | Yes | Yes | Yes |
| Viewing Dashboards | Yes | Yes | Yes |

---

## 9. Security Notes

> [!IMPORTANT]
> **Credential Encryption**: Vendor API keys/secrets are encrypted using AES-256 before storage in the database. They are only decrypted in-memory during real-time proxy calls or Celery tasks.

> [!WARNING]
> **Password Length**: Due to bcrypt limitations, passwords must be $\le 72$ characters. Enforced via Pydantic schema validation.