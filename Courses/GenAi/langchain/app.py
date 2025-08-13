import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ======== PDF Reading ========
def get_pdf_text(pdf_docs):
    """Extracts all text from a list of PDF files."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


# ======== Text Splitting ========
def get_text_chunks(text):
    """Splits text into manageable overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(text)
    return chunks


# ======== Vector Store Creation ========
def get_vector_store(text_chunks):
    """Creates and saves a FAISS vector store from text chunks."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


# ======== Conversational Chain ========
def get_conversational_chain():
    """Creates a LangChain QA chain with Gemini model."""
    prompt_template = """
    Answer the question as detailed as possible based ONLY on the provided context.
    If the answer is not in the context, just say: "Answer is not available in the context."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",   # ✅ Correct Gemini model name
        temperature=0.3
    )

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain


# ======== Main Streamlit App ========
def main():
    st.set_page_config(page_title="PDF Q&A with Gemini", layout="wide")
    st.title("📄 PDF Q&A Chatbot (Gemini)")

    # Sidebar PDF upload
    st.sidebar.header("Upload PDFs")
    pdf_docs = st.sidebar.file_uploader(
        "Upload your PDF files",
        accept_multiple_files=True,
        type=["pdf"]
    )

    if st.sidebar.button("Process PDFs"):
        if pdf_docs:
            with st.spinner("Processing PDFs..."):
                raw_text = get_pdf_text(pdf_docs)  # Extract text
                text_chunks = get_text_chunks(raw_text)  # Split into chunks
                get_vector_store(text_chunks)  # Save to FAISS
                st.session_state.processed = True
                st.success("✅ PDFs processed and stored!")
        else:
            st.warning("Please upload at least one PDF.")

    # Question answering section
    st.header("💬 Ask a Question from Your PDFs")
    if st.session_state.get("processed", False):
        user_question = st.text_input("Enter your question:")

        if st.button("Get Answer"):
            if user_question.strip():
                with st.spinner("Fetching answer..."):
                    # Load FAISS vector store
                    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                    vector_store = FAISS.load_local(
                        "faiss_index",
                        embeddings,
                        allow_dangerous_deserialization=True
                    )

                    # Retrieve relevant chunks
                    docs = vector_store.similarity_search(user_question)

                    # Run QA chain
                    chain = get_conversational_chain()
                    response = chain(
                        {"input_documents": docs, "question": user_question},
                        return_only_outputs=True
                    )

                    # Display answer
                    st.markdown("### 📌 Answer")
                    st.write(response["output_text"])
            else:
                st.warning("Please enter a question.")
    else:
        st.info("Upload and process PDFs first before asking questions.")


if __name__ == "__main__":
    main()
