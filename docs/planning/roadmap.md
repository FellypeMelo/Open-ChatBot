# Delivery Roadmap — Open-ChatBot Enterprise

## M01: Foundational Core (Current)
*   **Goal**: Establish the character engine and basic chat immersion.
*   **Deliverables**: 
    *   SQLite + SQLAlchemy Schema.
    *   State-to-Behavior Mapping Logic.
    *   Frontend Message Renderer (Italic/Bold).
*   **Success Metric**: 100% test pass on character consistency unit tests.

## M02: User Identity & Profile Persistence
*   **Goal**: Multi-session user recognition.
*   **Deliverables**: 
    *   User Profile CRUD.
    *   Pronoun/Name Injection in Master Prompt.
    *   Session-based chat history retrieval.
*   **Success Metric**: User is addressed by name in > 90% of start-of-session responses.

## M03: Advanced Memory (RAG)
*   **Goal**: Long-term context awareness.
*   **Deliverables**: 
    *   ChromaDB / FAISS Integration.
    *   Automated "Reflections" summarizing agent.
    *   Contextual Retrieval Logic.
*   **Success Metric**: AI references a fact from the "Reflection Store" in a relevant context.

## M04: Scalability & Compliance
*   **Goal**: Enterprise-grade infrastructure.
*   **Deliverables**: 
    *   PostgreSQL Migration.
    *   Redis Caching for Session States.
    *   LGPD/GDPR Data Deletion Bridge.
*   **Success Metric**: Throughput > 500 req/s with < 200ms overhead (excluding inference).
