# Smart Inventory: AI-Powered Inventory Management SaaS

This is an AI-enhanced, asynchronous inventory management system built with FastAPI and SQLModel. It features a complete suite of APIs for managing users, stores, products, and transactions, and includes an integrated incremental machine learning pipeline using the River library to predict stock levels in real-time.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python:** Version 3.10 or higher.
* **Poetry:** For dependency management. [Installation Guide](https://python-poetry.org/docs/#installation).
* **PostgreSQL:** A running instance of a PostgreSQL database.
* **Git:** For cloning the repository.

---

## 2. Local Setup and Installation

Follow these steps to get the application running on your local machine.

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd Smart-Inventory

Step 2: Configure Environment Variables
The application uses an .env file for configuration. A template is provided.

# Copy the example file to create your own local configuration
cp .env.example .env

Now, open the newly created .env file and update the DATABASE_URL to match your local PostgreSQL connection string.

# .env
DATABASE_URL="postgresql+asyncpg://YOUR_POSTGRES_USER:YOUR_POSTGRES_PASSWORD@localhost:5432/inventory"

Step 3: Install Dependencies
Poetry will handle installing all the necessary Python packages listed in pyproject.toml.

poetry install

Step 4: (Windows Only) Set PowerShell Execution Policy
If you are using PowerShell on Windows, you may need to allow local scripts to run. Open PowerShell as an Administrator and run the following command:

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

3. Database Setup
The application includes a script to initialize the database. This script will drop all existing tables, create new ones based on the models, and seed the database with default data (e.g., user roles and a default admin user).

Important: This is a destructive operation and will erase all data in the public schema.

# Run the database initialization and seeding script
poetry run init-db

After running this, your database will be ready, and a default super admin user will be created with the following credentials:

Email: admin@example.com

Password: test@123

4. Running the Application
Once the setup is complete, you can run the application using the Uvicorn ASGI server.

# Start the server with auto-reload enabled
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The application will now be running and accessible on your local machine.

5. Accessing the Application
Here are the key URLs to interact with the running application:

API Interactive Docs (Swagger UI):
http://localhost:8000/api/v1/docs

Alternative API Docs (ReDoc):
http://localhost:8000/api/v1/redoc

Health Check Endpoint:
http://localhost:8000/healthz

ML Prediction Endpoint Example:
http://localhost:8000/api/v1/ml/predict-stock/{store_id}/{product_id}

6. Running Automated Tests
The project is set up with pytest. To run the test suite and ensure everything is working as expected:

# Activate the poetry shell
poetry shell

# Run pytest
pytest
