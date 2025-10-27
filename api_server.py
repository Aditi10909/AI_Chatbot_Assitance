import os
import shutil
from typing import List
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from src.data_loader import load_all_documents   # should accept folder path like "data"
from src.vectorstore import FaissVectorStore     # must provide build_from_documents or similar
from src.search import RAGSearch                 # must provide search_and_summarize
from src.report import build_pdf_in_memory, parse_sections_from_query, enumerate_available_sections, collect_sections_from_data

app = FastAPI(title="RAG Assistant Simple API")

# CONFIG
UPLOAD_DIR = "data"         
FAISS_DIR = "faiss_store"   
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)


# Allow all origins for quick testing (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple models for request bodies
class AskRequest(BaseModel):
    query: str
    top_k: int = 3

class ProcessResponse(BaseModel):
    status: str
    message: str

class GenerateReportRequest(BaseModel):
    query: str
    top_k: int = 3 

# HEALTH
@app.get("/health")
def health():
    return {"status": "ok"}

# UPLOAD files endpoint
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    """
    Save uploaded files into the UPLOAD_DIR ("data") so that load_all_documents("data") can see them.

    """
    saved = []
    for f in files:
        dest_path = os.path.join(UPLOAD_DIR, f.filename)
        # save file bytes
        with open(dest_path, "wb") as out:
            contents = await f.read()
            out.write(contents)
        saved.append(dest_path)
    return {"saved_files": saved}

# BACKGROUND processing helper
def _process_all_files():
    # 1) load documents from the data folder
    docs = load_all_documents(UPLOAD_DIR)

    # 2) build vector store (this should create or overwrite faiss files in FAISS_DIR)
    store = FaissVectorStore(FAISS_DIR)
    store.build_from_documents(docs)

# PROCESS endpoint (starts background task)
@app.post("/process", response_model=ProcessResponse)
def process(background_tasks: BackgroundTasks):
    """
    Trigger processing (ingest & index) of files already present in the `data` folder.
    This runs as a background task so the endpoint returns quickly.
    """
    # quick sanity check: are there files?
    files = os.listdir(UPLOAD_DIR)
    if not files:
        raise HTTPException(status_code=400, detail="No files found in the data folder. Upload files first.")
    background_tasks.add_task(_process_all_files)
    return {"status": "processing_started", "message": f"Found {len(files)} files; processing in background."}

# ASK endpoint
@app.post("/ask")
def ask(req: AskRequest):
    """
    Run the RAG search & summarize pipeline and return JSON.
    It mirrors what your Streamlit does:
      rag_search = RAGSearch()
      summary = rag_search.search_and_summarize(query, top_k=3)
    """
    # Basic check: ensure index exists (best-effort)
    # If FaissVectorStore persists files to FAISS_DIR, we can detect presence
    faiss_files_exist = any(fname.endswith(".faiss") or fname.endswith(".pkl") for fname in os.listdir(FAISS_DIR))
    # Not fatal: let RAGSearch itself handle missing index and raise if necessary
    rag = RAGSearch()

    try:
        result = rag.search_and_summarize(req.query, top_k=req.top_k)
    except Exception as e:
        # Return an informative error (instead of 500 trace)
        raise HTTPException(status_code=500, detail=f"RAG search failed: {e}")

    # Normalize result into a JSON-friendly response
    if isinstance(result, str):
        return {"answer": result}
    elif isinstance(result, dict):
        # return the dict as-is (ensure values are JSON serializable)
        return result
    else:
        # fallback: convert to string
        return {"answer": str(result)}

# Simple file download listing (optional helper)
@app.get("/uploads")
def list_uploads():
    files = os.listdir(UPLOAD_DIR)
    return {"uploads": files}


@app.post("/generate_report")
def generate_report(req: GenerateReportRequest):
    """
    Generate a new PDF containing the sections requested in the natural-language query.
    Returns a StreamingResponse with application/pdf and a JSON header indicating missing sections if any.
    """
    # 1) Enumerate available sections across uploaded docs
    available_sections = enumerate_available_sections(UPLOAD_DIR)  # from helpers

    # 2) Parse query to get requested section names
    requested_found, requested_missing = parse_sections_from_query(req.query, available_sections)

    # If nothing found: return 400 with info (user ambiguous)
    if not requested_found:
        return {"error": "No requested sections detected from query.", "available_sections": available_sections}

    # 3) Collect text from uploaded docs for all requested_found
    sections_text = collect_sections_from_data(UPLOAD_DIR, requested_found)

    # 4) Build PDF bytes
    try:
        pdf_bytes = build_pdf_in_memory(sections_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    # 5) Return as StreamingResponse and include missing section info in header/JSON (we'll add JSON in body)
    # We'll return the PDF bytes directly. To notify frontend about missing sections, return a multipart-like response is complex;
    # Instead, we use a helper JSON endpoint approach: include missing info in response headers.
    headers = {}
    if requested_missing:
        headers["X-Missing-Sections"] = ",".join(requested_missing)

    # Use StreamingResponse to stream pdf bytes
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@app.get("/")
def home():
    return {"message": "✅ API is running! Visit /docs to test endpoints."}


# To run: uvicorn api_server:app --reload --port 8000