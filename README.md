## System Architecture 

```mermaid
flowchart TD
  %% User & API
  A["User / Streamlit UI"] --> B["FastAPI Backend"]

  %% Pipeline (vertical)
  subgraph PIPE["Processing Pipeline"]
    direction TB
    B --> C["Data Loader\n(extract text, tables)"]
    C --> D["Embedder\n(generate embeddings)"]
    D --> E["VectorStore\n(FAISS)"]
    E --> F["RAGSearch\n(retrieve + LLM)"]
    F --> G["Report Generation\n(assemble sections)"]
  end

  G --> H["Generated Report\n(PDF)"]
  H -->|Download| A

  %% Styling
  classDef ingest fill:#E0F7E9,stroke:#1B5E20,color:#000;
  classDef retrieve fill:#EDE7F6,stroke:#4A148C,color:#000;
  classDef report fill:#FFF8E1,stroke:#F57F17,color:#000;
  classDef user fill:#E3F2FD,stroke:#1565C0,color:#000;

  class C,D,E ingest;
  class F retrieve;
  class G,H report;
  class A,B user;
