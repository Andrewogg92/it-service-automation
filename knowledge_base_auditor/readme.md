# Self-Healing Knowledge Base Auditor

## System Overview

This system is an AI-driven knowledge base automation pipeline designed to evaluate support ticket resolution notes, determine whether existing documentation already exists in a structured knowledge index, and conditionally generate new knowledge base articles when needed. The system maintains persistent state through a PostgreSQL backend and logs execution outcomes for observability and auditability.

This folder contains the orchestration blueprint and database schemas for the AI Auditor and Drafter system.

### Contents
*   **`mlb_kb_auditor_v2.json`**: The complete Make.com blueprint. This includes the webhook ingestion, PostgreSQL search queries, two-tier AI routing, Google Docs creation, and Try/Catch error handling.
*   **`/database`**: Contains the `.sql` scripts used to generate the Supabase (PostgreSQL) tables for the search index, execution logs, and error logs.
*   **`/assets`**: Contains screenshots of the workflow logic, Supabase tables, and AI-generated documents.

### How to View the Architecture
1. Download the `.json` blueprint file.
2. Create a new scenario in [Make.com](https://www.make.com/).
3. Click the `...` (More) menu at the bottom and select **Import Blueprint**.
4. *Note: You will need to map your own Supabase, OpenAI, and Google Drive API connections for the modules to execute.*
