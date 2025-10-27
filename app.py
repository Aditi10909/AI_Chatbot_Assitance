import streamlit as st 
from src.data_loader import load_all_documents 
from src.vectorstore import FaissVectorStore 
from src.search import RAGSearch 

def main(): 
    st.set_page_config("AI-powered assistant") 
    st.header("Upload any files and chat")
    with st.sidebar: 
        st.title("Menu:") 
        data = st.file_uploader("Upload any type of files and Click on the submit & Process Button", accept_multiple_files=True) 
        if st.button("Submit & Process"): 
            with st.spinner("Processing..."): 
                docs = load_all_documents("data") 
                store = FaissVectorStore("faiss_store") 
                store.build_from_documents(docs) 
    
    query = st.text_input("Ask a question from the files") 
    if query: 
        rag_search = RAGSearch() 
        # Run the search/summarize 
        summary = rag_search.search_and_summarize(query, top_k=3) 
        try: 
            preview = summary if isinstance(summary, str) else repr(summary)[:1000] 
            st.write(preview) 
        except Exception: 
            st.write("Could not preview summary safely.") 
            
        # Normalize the result to a displayable string safely 
        if isinstance(summary, dict):
             # Try common keys that might hold the text 
             output = (
                  summary.get("output_text") 
                  or summary.get("text") 
                  or summary.get("summary") 
                  or summary.get("answer") 
                  or str(summary) 
                  ) 
        else: 
            # If it's already a string or other object, convert to string 
            output = str(summary) 
            
        # st.write("Reply:", output) 
if __name__ == "__main__": 
    main()