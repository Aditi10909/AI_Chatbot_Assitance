## 🧰 Tech Stack Description

### **1. Programming Language**

**Python 3.13**  
Used as the primary programming language for both backend and frontend logic.  
Python’s ecosystem provides extensive support for AI, document processing, and web frameworks.

---

### **2. Frameworks and Core Components**

| Layer | Framework / Library | Purpose |
|--------|----------------------|----------|
| **Frontend (UI)** | **Streamlit** | Provides an intuitive web interface where users can upload files, enter queries, and download generated reports. |
| **Backend (API)** | **FastAPI** | Handles file uploads, query requests, report generation, and communication between the frontend and backend. Offers asynchronous request handling and clean API design. |
| **AI Reasoning & Retrieval** | **Llama** | Interprets user queries, extracts section names, and performs context-based reasoning using Retrieval-Augmented Generation (RAG). |
| **Vector Database** | **FAISS (Facebook AI Similarity Search)** | Efficiently stores and retrieves document embeddings for semantic search and similarity lookups. |
| **Document Parsing** | **python-docx**, **PyMuPDF (fitz)** | Extracts text, tables, and metadata from DOCX and PDF files for indexing and report generation. |
| **Report Creation** | **FPDF / ReportLab** | Dynamically generates downloadable PDF reports, combining extracted sections, tables, and summaries. |
| **Data Processing** | **pandas**, **numpy** | Handles tabular data (e.g., tables extracted from documents or embeddings). |

---

### **3. Machine Learning / NLP Components**

| Component | Description |
|------------|-------------|
| **Embedder** | Converts document text chunks into dense vector embeddings (using SentenceTransformers, OpenAI Embeddings, or similar). |
| **VectorStore (FAISS)** | Performs fast nearest-neighbor search to find semantically relevant content. |
| **RAGSearch Module** | Combines the retrieval (via VectorStore) with LLM reasoning (via Llama model) to generate accurate and context-aware responses. |
| **Query Parser** | Uses Llama or simple heuristics to extract specific report sections (e.g., “Introduction”, “Findings”, “Summary”) from user queries. |

---

### **4. Deployment and Storage**

| Layer | Technology | Purpose |
|--------|-------------|----------|
| **Local/Cloud Hosting** | **Uvicorn / FastAPI server** | Runs the backend API locally or deploys it on cloud platforms like Render, Railway, or HuggingFace Spaces. |
| **Frontend Hosting** | **Streamlit Cloud / Local Streamlit Run** | Simple deployment for interactive UI. |
| **File Storage** | **Local `data/` directory** | Stores uploaded user documents for processing. |
| **Index Storage** | **`faiss_store/` directory** | Persists FAISS index files and metadata for reuse between sessions. |

---

### **5. Supporting Tools**

- **Requests** — Handles API calls between Streamlit (frontend) and FastAPI (backend).  
- **uvicorn** — ASGI server for running FastAPI applications.    
- **Git & GitHub** — Version control and collaboration platform for hosting and documenting code.

---

### **6. System Integration Summary**

| Layer | Technology | Role |
|--------|-------------|------|
| **Interface** | **Streamlit** | User-facing upload and query interface. |
| **API Layer** | **FastAPI** | Routes all operations between UI, ML models, and report generator. |
| **Core Intelligence** | **Llama + RAGSearch + FAISS** | Understands queries, retrieves information, and composes meaningful outputs. |
| **Document Handling** | **python-docx, PyMuPDF** | Extracts content and structure from input documents. |
| **Report Builder** | **FPDF / ReportLab** | Creates formatted, downloadable reports. |
| **Storage** | **Local / FAISS** | Persists uploaded files and indexes. |

---

### **7. Deployment Environment**

- **Local Environment:**  
  Python virtual environment (`.venv`) with all dependencies listed in `requirements.txt`.

- **Web Server:**  
  Runs via:  
  ```bash
  uvicorn api_server:app --reload --port 8000


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

