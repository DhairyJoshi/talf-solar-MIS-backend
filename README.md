# Talf Solar MIS Backend

Talf Solar MIS is a Management Information System designed to track performance, financial revenue, and technical KPIs for solar portfolios. This backend provides a robust API to replace prototype mock services with real-world database persistence and multi-vendor inverter integrations.

## Prerequisites

Before setting up the application, ensure you have the following installed:

- Python 3.9 or higher
- PostgreSQL (for relational data storage)
- Redis (for Celery task queuing)

## Installation

1. Clone the repository to your local machine.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The application uses an `.env` file for configuration. A template is provided in the root directory. Ensure the following variables are set correctly for your local environment:

- `DATABASE_URL`: PostgreSQL connection string (asyncpg driver required).
- `REDIS_URL`: Connection string for the Redis broker.
- `SECRET_KEY`: Used for JWT token generation.
- `ENCRYPTION_KEY`: A 32-byte Fernet key used for encrypting vendor API credentials at rest.

## Database Setup

Initialize the database schema using Alembic migrations:
```bash
alembic upgrade head
```

## Running the Application

To run the full system, you need to start the API server and the background worker.

### 1. Start the API Server
```bash
uvicorn app.main:app --reload
```
The server will be available at `http://localhost:8000`.

### 2. Start the Celery Worker
```bash
celery -A app.worker.celery_app worker --loglevel=info
```
The worker handles scheduled tasks, such as the nightly 02:00 IST synchronization of inverter data.

## Documentation Reference

The project includes detailed documentation for different aspects of the system:

- [Architecture Overview](ARCHITECTURE.md): System diagram and component breakdown.
- [Database Schema](DATABASE_SCHEMA.md): Entity Relationship Diagram (ERD) and table details.
- [API Documentation](API_DOCUMENTATION.md): Comprehensive reference for all REST endpoints.
- [Integration Strategy](INTEGRATION_STRATEGY.md): Guide for adding new inverter vendors using the Adapter Pattern.

## API Access

Once the server is running, you can access the interactive Swagger documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
