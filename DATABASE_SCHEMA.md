# Database Schema Design

This document details the relational database schema for the Talf Solar Management Information System.

## Entity Relationship Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role
        datetime created_at
        datetime updated_at
    }

    PROJECTS {
        int id PK
        string name
        string location
        float capacity_kw
        datetime created_at
        datetime updated_at
    }

    INVERTERS {
        int id PK
        int project_id FK
        int module_build_id FK
        string serial_number UK
        string vendor_type
        string encrypted_credentials
        datetime created_at
        datetime updated_at
    }

    MODULE_BUILDS {
        int id PK
        string manufacturer
        string model_name
        float rated_power_wp
        float degradation_rate_pct
        datetime created_at
    }

    MONTHLY_DATA {
        int id PK
        int project_id FK
        string month
        float energy_kwh
        float irradiation_kwh_m2
        float revenue
        float tariff_rate
        datetime created_at
        datetime updated_at
    }

    MONTHLY_KPIS {
        int id PK
        int project_id FK
        string month
        float total_yield_kwh
        float pr_percentage
        float cuf_percentage
        float target_p50_kwh
        float revenue
        float irradiation_kwh_m2
        datetime computed_at
    }

    BREAKDOWN_EVENTS {
        int id PK
        int inverter_id FK
        datetime start_date
        datetime end_date
        string description
        float loss_kwh
        datetime created_at
    }

    PROJECTS ||--o{ INVERTERS : "contains"
    PROJECTS ||--o{ MONTHLY_DATA : "has manual entries"
    PROJECTS ||--o{ MONTHLY_KPIS : "aggregates"
    MODULE_BUILDS ||--o{ INVERTERS : "linked to"
    INVERTERS ||--o{ BREAKDOWN_EVENTS : "records"
```

## Entity Details

### Users
Stores administrative and operational user accounts. Roles include ADMIN, OPERATIONS, and VIEWER to enforce access control.

### Projects
The top-level entity representing a solar installation. It acts as a container for inverters and aggregated performance data.

### Inverters
Represents individual solar inverters. Holds encrypted credentials for third-party API communication (SolisCloud, Sungrow, etc.) and is linked to a specific project.

### Module Builds
Templates for solar panel configurations. These define technical specifications like degradation rates, which are essential for calculating theoretical energy targets.

### Monthly Data
Stores manual data entries or bulk-uploaded CSV records for a project's monthly performance (energy, irradiation, and revenue).

### Monthly KPIs
Stores pre-calculated Performance Ratio (PR), Capacity Utilisation Factor (CUF), and P50 targets. This table ensures fast dashboard loading by avoiding on-the-fly complex calculations.

### Breakdown Events
Logs downtime or fault occurrences for specific inverters, including estimated energy loss and maintenance descriptions.