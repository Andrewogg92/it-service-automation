# Ticket Triage & Routing Engine

## What this does

Incoming support tickets come in through different channels and used to get manually sorted and routed. This system automates that. When a ticket comes in via webhook, it gets passed to GPT, which classifies it by issue type and urgency, and routes it to the right queue automatically. Results get logged to a staging database for ServiceNow integration.

## What's in this repo

- `mlb_triage_engine_v1.json` — the Make.com blueprint. Import this directly into a Make.com workspace to replicate the full workflow.
- `/assets` — screenshots of the workflow canvas and database logs.

## How to run it

1. Download the `.json` file
2. Create a new scenario in Make.com
3. Click the `...` menu and select Import Blueprint
