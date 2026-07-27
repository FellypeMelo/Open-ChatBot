# Data Privacy Compliance (GDPR & LGPD)

Open-ChatBot is fully offline by default, aligning with the principles of data minimization and privacy-by-design under the Brazilian General Data Protection Law (LGPD) and General Data Protection Regulation (GDPR).

## 1. Data Inventory (Personally Identifiable Information - PII)
The application stores the following local identifiers:
*   **User Profile Data:** Name, gender (stored in SQLite `users` table).
*   **Conversational Data:** Chat messages, thoughts, actions, timestamps, and character diaries (stored in `message_nodes` and `journal_entries` tables).
*   **Embeddings Data:** High-dimensional vector hashes of messages and lore (stored locally in `/chroma_db`).

## 2. LGPD & GDPR Core Compliance Pillars

### A. Principle of Local Sovereignty (Zero Data Sharing)
All PII is persisted in the local SQLite database (`chatbot.db`) and local TurboVec store. No user data is transmitted to cloud APIs or remote servers. All model inference runs on the local CPU/GPU using llama.cpp.

### B. Right to Erasure / Right to be Forgotten (Art. 16 LGPD / Art. 17 GDPR)
Users have full command over their data. 
*   **Database Purging:** Deleting the local database file (`chatbot.db`) and the local vector store directory (`/chroma_db`) immediately and permanently purges all logs.
*   **Chat History Clearing:** Clearing conversations via the UI invokes [clear_chat_history](../../../src/backend/api/chat.py) which explicitly executes SQL `DELETE` queries on `message_nodes` and `journal_entries` for the selected character, resetting state metadata immediately.

### C. Accountability (Art. 37 LGPD)
Actions are locally trace-logged with a `request_id` context to verify the system flows. No telemetry or telemetry logs are leaked outside the system.
