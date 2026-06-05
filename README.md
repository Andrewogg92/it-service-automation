# ⚾ Enterprise IT Service Automation Suite

This repository contains a portfolio of event-driven AI and data-automation systems designed for IT  operations.

I designed and built these systems to solve three core business problems:
1.  **Forecasting** team capacity against dynamic business and travel schedules.
2.  **Automating** manual ticket dispatching and triage.
3.  **Eliminating** repetitive documentation workflows through a self-healing knowledge base.

The suite leverages a modern data stack, including Python, PostgreSQL (Supabase), event-driven webhooks (Make.com), and stateful AI orchestration.

---

## **Project 1: Workforce Capacity & Demand Planner (Flagship Project)**

**Folder:** `/capacity-demand-planner`

### **The Problem**

Forecasting IT support capacity is often a manual, spreadsheet-driven process that fails to account for the overlapping, dynamic nature of corporate travel, PTO, and fluctuating ticket volumes. This leads to inaccurate staffing estimates and puts service levels at risk.

### **The Architecture & Solution**

*   **Relational Database Core:** Built a normalized PostgreSQL database (Supabase) to serve as the single source of truth for all staffing, demand, and scheduling data.
*   **Dynamic Capacity Calculation:** The system ingests master travel and event calendars and automatically performs daily capacity deductions. It correctly calculates the impact of multiple analysts being unavailable on the same day due to overlapping events.
*   **Remote Calculation Engine:** A Flask API, deployed on PythonAnywhere, receives webhook data and executes the core mathematical forecasting logic, processing thousands of records to calculate daily team utilization and staffing gaps.
*   **Interactive "What-If" Simulation:** The Streamlit frontend includes a demand multiplier slider, allowing leaders to instantly simulate the impact of a 30% spike in service demand without altering the underlying database.
*   **AI-Generated Executive Briefings:** After the math is complete, an AI layer generates a concise, natural-language summary of the weekly capacity outlook, highlighting key risks and trends.

### **Visual Architecture**
<img width="796" height="536" alt="Screenshot 2026-06-05 at 12 57 23 PM" src="https://github.com/user-attachments/assets/b635be35-d0b4-4a28-897a-f26df14ea242" />

This system uses a multi-layered architecture where a Streamlit dashboard triggers a Make.com webhook, which pulls live data from Supabase, sends it to a Python Flask API for heavy computation, and returns a complete, visualized forecast with an AI summary back to the user—all in real-time.

<img width="1895" height="881" alt="image" src="https://github.com/user-attachments/assets/d0c64184-57f6-43bf-b138-439042e7572c" />


### **The Impact**

*   **Provides 100% data-driven, mathematically sound weekly staffing forecasts.**
*   Eliminates manual spreadsheet work and subjective capacity planning.
*   Gives leadership an instant, interactive tool to simulate high-demand scenarios and make proactive staffing decisions.

---

## Project 2: Omni-Channel Ticket Triage Engine

**Folder:** `/omnichannel_triage_engine`

### The Problem

Support requests arrive unstructured from multiple inbound channels (inbound emails, Zoom Contact Center inbound calls, Slack messages, etc.), requiring human analysts to read, classify, and manually triage and generate every single ticket.

### The Architecture & Solution

* **Normalized Ingestion:** Built a webhook-driven ingestion system to catch unstructured inbound support events.
* **AI Classification:** Leveraged OpenAI (GPT-4o) with a custom system prompt to analyze the payload, classify the issue type (INC or REQ), and map it to the organization's internal taxonomy.
* **Deterministic Formatting:** Utilized strict JSON parsing layers to enforce deterministic outputs, ensuring the payload is properly structured for downstream routing.
* **Observability:** Logged all classification outcomes into a mock staging database (Google Sheets) designed to map 1:1 with ServiceNow schemas.

### Visual Architecture
![Omni-Channel Triage Workflow](./omnichannel_triage_engine/assets/triage_flow_canvas.png)
This scenario ingests inbound support events, classifies requests using GPT-4o, validates deterministic JSON outputs, and routes structured payloads into a mock ServiceNow staging layer for downstream handling.

### The Impact

* **Eliminated ~8-9 hours of manual ticket triage per week.**
* Achieved instantaneous, zero-touch ticket routing to the correct resolution queues.

---

## Project 3: Self-Healing Knowledge Base Auditor

**Folder:** `/knowledge_base_auditor`

### The Problem

When a large Knowledge Base (KB) grows outdated, support analysts spend many hours manually drafting net-new, updating existing, or revising/deprecating outdated KB articles.

### The Architecture & Solution

* **Programmatic Knowledge Retrieval:** Transitioned the team from slow, manual Confluence searches to an automated, high-speed PostgreSQL (Supabase) index. This custom database layer programmatically caches existing KB metadata, allowing the AI to instantly query prior resolutions before taking action.
* **Two-Tier AI Routing:**
  * **Tier 1 (The Auditor):** Extracts keywords from inbound ticket resolutions, queries the database, and deterministically decides if a duplicate KB exists. If it does, the workflow halts.
  * **Tier 2 (The Drafter):** If no KB exists, the AI autonomously drafts a new, formatted Wiki in Google Docs.
* **The "Self-Healing" Loop:** AAutomatically indexes newly generated AI drafts back into the PostgreSQL database, allowing future workflows to identify and prevent duplicate KB generation.
* **Reliability & Error Handling:** Built comprehensive Try/Catch error-handler routes around volatile OpenAI endpoints, reducing workflow interruptions caused by API failures.

### Visual Architecture
![Knowledge Base Auditor Workflow](./knowledge_base_auditor/assets/auditor_flow_canvas.png)
This orchestration pipeline processes resolution notes extracted from support tickets, checks a PostgreSQL knowledge index for existing documentation, and conditionally generates new knowledge base articles when no match is found, while logging execution state and API errors for observability.

### Business Impact

* **Eliminated an estimated 20-30 hours of manual documentation toil per month.**
* Ensured 100% documentation coverage for new issues while preventing duplicate work.

---

## Database Schemas (Supabase / PostgreSQL)

This architecture relies on persistent state management to track execution logic, halt redundant workflows, and log API failures. Below are the core table schemas powering the observability layer.

### 1. Execution Logs (Audit Trail)

Tracks every decision made by the Tier 1 AI Auditor, providing a clear ROI metric on redundant drafts prevented.

```sql
CREATE TABLE execution_logs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  ticket_id VARCHAR(255),
  status VARCHAR(255),
  ai_verdict TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);
