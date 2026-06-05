# Workforce Capacity & Demand Planner

This folder contains the source code for a dynamic, multi-system IT workforce capacity and demand forecasting engine.

---

## Technical Architecture & Data Flow

This system is built on a decoupled, event-driven architecture that separates the user interface from the backend calculation engine.

1.  **Frontend (Streamlit):** The user interacts with the `app.py` dashboard. When the "Generate" button is clicked, it sends a simple JSON payload containing a `multiplier` to a Make.com webhook URL.

2.  **Automation & ETL (Make.com):** The Make.com webhook triggers a scenario that performs the Extract-Transform-Load (ETL) process:
    *   **Extract:** It queries a PostgreSQL database (Supabase) to pull four key tables: `employees`, `demand_history`, `task_weights`, and `calendar_events`.
    *   **Transform:** It structures these four arrays and the `multiplier` into a single, clean JSON object.
    *   **Load:** It sends this final JSON payload via an HTTP POST request to a remote Python API.

3.  **Backend Calculation (Flask on PythonAnywhere):** The `flask_app.py` script, hosted on a cloud server, receives the data. It performs the heavy mathematical lifting:
    *   Parses the data arrays.
    *   Calculates baseline capacity from the number of employees.
    *   Loops through the `calendar_events` and `employee_availability` tables to find overlapping travel/PTO and deducts capacity for each day.
    *   Calculates daily demand by multiplying `demand_history` volumes by the `task_weights`.
    *   Returns a final JSON object containing the `forecast_results` and `weekly_summary`.

4.  **Visualization (Streamlit):** The `app.py` dashboard receives the final calculations from the Flask API and uses Plotly and Pandas to render the interactive charts and data tables.

---

## File Descriptions

*   `app.py`: The frontend dashboard built with Streamlit. This file is responsible for UI rendering and making the initial API call to the Make.com webhook.
*   `flask_app.py`: The backend API built with Flask. This script contains all the business logic and mathematical calculations for the capacity forecast. It is designed to be deployed on a server like PythonAnywhere.
*   `requirements.txt`: A list of the necessary Python packages (`streamlit`, `pandas`, `requests`, `plotly`, `flask`) required to run this project.
*   `/assets/`: Contains visual assets like screenshots of the dashboard and database schemas for documentation purposes.

---

### **Configuration**

To run this project, the following placeholders must be replaced with production values:

*   In `app.py`: The `make_webhook_url` variable must be replaced with a real Make.com webhook URL.
*   The Make.com scenario must be configured with the correct Supabase database credentials and the URL for the deployed Flask API.

