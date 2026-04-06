# Talf Solar MIS: System Architecture

This diagram illustrates the flow of data and control between the core components of the system.

```mermaid
graph TD
    %% Users and Frontend
    User((User/Admin)) -->|HTTPS| React[Frontend: React/Tailwind]
    
    %% API Layer
    React <-->|REST API + JWT| FastAPI[Backend: FastAPI]
    
    subgraph "FastAPI Application"
        Router[API Routers: Auth, Projects, Inverters]
        Auth[RBAC: ADMIN/OPS/VIEWER]
        Proxy[Proxy Layer: Live Status/Curve]
        Calc[KPI Calculation Engine]
    end
    
    %% Database and Storage
    FastAPI <-->|SQLAlchemy Async| Postgres[(PostgreSQL DB)]
    
    %% Background Processing
    FastAPI -->|Enqueue Task| Redis{Redis Broker}
    Redis -->|Process| Celery[Celery Worker]
    Celery <-->|Store/Read| Postgres
    Celery -->|Run Formulas| Calc
    
    %% External Integration
    Proxy <-->|Short-lived Auth| ExtAPIs[External Inverter APIs]
    Celery <-->|Scheduled Sync| ExtAPIs
    
    subgraph "External Providers"
        ExtAPIs --- Solis[SolisCloud]
        ExtAPIs --- Sungrow[iSolarCloud]
        ExtAPIs --- TrackSO[TrackSO IoT]
    end
    
    %% Styling
    classDef primary fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef secondary fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef external fill:#f1f8e9,stroke:#1b5e20,stroke-width:2px;
    
    class React,FastAPI primary;
    class Celery,Calc,Proxy secondary;
    class Postgres,Redis storage;
    class Solis,Sungrow,TrackSO external;
```

---

## Component Breakdown

### 1. Frontend (React/Tailwind)
- **Roles**: Dashboard visualization, data entry forms, and user management.
- **Auth**: Manages JWT tokens for session persistence.

### 2. Backend (FastAPI)
- **Roles**: Exposes REST endpoints, validates schemas (Pydantic), and enforces Role-Based Access Control.
- **Proxy**: Bypasses CORS and securely injects encrypted vendor credentials for real-time status.

### 3. Database (PostgreSQL)
- **Roles**: Long-term storage of project metadata, encrypted API keys, manual energy entries, and pre-calculated KPIs.

### 4. Task Queue (Redis + Celery)
- **Roles**: Handles time-consuming operations (like fetching 12 months of historical data) off the main request-response cycle to keep the UI responsive.
- **Scheduler**: Triggers the **02:00 IST** nightly sync.

### 5. External APIs
- **Roles**: Third-party sources for raw solar yield. The system acts as a standardizing middleware for these disparate data sources.
