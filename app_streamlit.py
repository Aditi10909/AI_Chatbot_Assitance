import streamlit as st
import requests

#  Set API URL 
API_URL = "http://127.0.0.1:8000"

def upload_files(files):
    """Send uploaded files to backend API."""
    uploaded_files = [("files", (f.name, f.getvalue(), f.type)) for f in files]
    response = requests.post(f"{API_URL}/upload", files=uploaded_files)
    return response.json()

def process_files():
    """Trigger document processing (index creation)."""
    response = requests.post(f"{API_URL}/process")
    return response.json()

def ask_question(query):
    """Send user question to backend and return answer."""
    payload = {"query": query, "top_k": 3}
    response = requests.post(f"{API_URL}/ask", json=payload)
    return response.json()

def generate_report(query):
    """Send user query to backend and return report"""
    payload = {"query": query, "top_k":3}
    response = requests.post(f"{API_URL}/generate_report", json = payload, stream=True)
    if response.status_code != 200:
        try:
            return {"error": response.json()}
        except Exception:
            return {"error": f"Status {response.status_code}: {response.text}"}
    # read bytes
    pdf_bytes = response.content
    missing = response.headers.get("X-Missing-Sections", "")
    missing_list = [m for m in missing.split(",") if m] if missing else []
    return {"pdf": pdf_bytes, "missing": missing_list}

def main():
    st.set_page_config("AI-powered assistant")
    st.header("Upload any files and chat")

    # --- Sidebar for uploads ---
    with st.sidebar:
        st.title("Menu:")
        files = st.file_uploader(
            "Upload any type of files and click Submit & Process",
            accept_multiple_files=True
        )

        if st.button("Submit & Process"):
            if files:
                with st.spinner("Uploading files..."):
                    res_upload = upload_files(files)
                    st.success(f"✅ Uploaded {len(res_upload.get('saved_files', []))} files")
                with st.spinner("Processing..."):
                    res_proc = process_files()
                    st.info(res_proc.get("message", "Processing started."))
            else:
                st.warning("Please upload at least one file before processing.")

    # --- Chat section ---
    query = st.text_input("Ask a question from the files (or request a report, e.g. 'Generate Introduction and Summary')")
    if query:
        cols = st.columns([1,1,1])
        if cols[0].button("Ask (chat)"):
            with st.spinner("Thinking..."):
                res = ask_question(query)
                answer = res.get("answer") or res.get("summary") or "No response."
                st.subheader("Assistant's Reply:")
                st.write(answer)
                if res.get("alert"):
                    st.warning("⚠️ Alert: The system detected an important condition.")
        if cols[1].button("Generate & Download Report"):
            with st.spinner("Generating report..."):
                res = generate_report(query)
            if res.get("error"):
                st.error(f"Report generation failed: {res['error']}")
            else:
                pdf_bytes = res["pdf"]
                missing = res["missing"]
                if missing:
                    st.warning(f"The following requested sections were *not found* in uploaded documents: {', '.join(missing)}")
                st.success("Report generated ✅")
                # Provide a download button
                st.download_button(
                    label="Download generated report (PDF)",
                    data=pdf_bytes,
                    file_name="generated_report.pdf",
                    mime="application/pdf"
                )

    

if __name__ == "__main__":
    main()
