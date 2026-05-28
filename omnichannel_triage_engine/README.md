# Omni-Channel Ticket Triage Engine

## System Overview

This system is an event-driven AI classification and routing engine that ingests unstructured support requests from multiple channels, normalizes incoming data via webhooks, and uses an LLM-based classifier to determine issue type and routing destination. Structured outputs are generated using deterministic JSON parsing and logged into a staging database for downstream ITSM integration.

This folder contains the core assets for the AI classification and routing engine.

### Contents
*   **`mlb_triage_engine_v1.json`**: The Make.com blueprint. You can download this file and import it directly into your Make.com workspace to replicate the entire webhook-to-AI-to-database flow.
*   **`/assets`**: Contains high-resolution screenshots of the workflow canvas and the staging database logs.

### How to View the Architecture
1. Download the `.json` blueprint file.
2. Create a new scenario in [Make.com](https://www.make.com/).
3. Click the `...` (More) menu at the bottom and select **Import Blueprint**.
