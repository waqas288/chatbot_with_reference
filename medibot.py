import os
import streamlit as st

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_groq import ChatGroq


## Uncomment the following files if you're not using pipenv as your virtual environment manager
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Page Configuration
st.set_page_config(
    page_title="MediBot - Your AI Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main Gradient Header */
    .main-header {
        background: linear-gradient(to right, #4b6cb7, #182848);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #e0e0e0;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #262730; /* Dark sidebar */
        border-right: 1px solid #444;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Feature Cards */
    .feature-card {
        background-color: #262730; /* Dark card background */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        border: 1px solid #444;
        color: white; /* Ensure text is white */
    }
    .feature-card h4 {
        color: #4b6cb7; /* Accent color for headings */
        margin-bottom: 5px;
    }
    .feature-card p {
        color: #e0e0e0;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #444;
        color: #888;
    }
    
    /* Hide Streamlit default menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

DB_CHROMA_PATH="vectorstore/db_chroma"
@st.cache_resource
def get_vectorstore():
    embedding_model=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db=Chroma(persist_directory=DB_CHROMA_PATH, embedding_function=embedding_model)
    return db


def set_custom_prompt(custom_prompt_template):
    prompt=PromptTemplate(template=custom_prompt_template, input_variables=["context", "question"])
    return prompt


def load_llm(huggingface_repo_id, HF_TOKEN):
    llm=HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        model_kwargs={"token":HF_TOKEN,
                      "max_length":"512"}
    )
    return llm


def main():
    # Sidebar
    with st.sidebar:
        st.title("🩺 MediBot Config")
        st.markdown("---")
        
        # File Upload
        st.subheader("📁 Data Source")
        uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=['pdf', 'txt', 'docx'])
        if uploaded_file:
            st.success(f"Loaded: {uploaded_file.name}")
        
        st.markdown("---")
        
        # Model Settings
        st.subheader("🧠 Model Settings")
        model_option = st.selectbox(
            "Choose Model",
            ("Llama 3 (Groq)", "Mistral 7B (HF)", "GPT-4o (OpenAI)")
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
        
        st.markdown("---")
        
        # Actions
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 🔗 Connect")
        st.markdown("[GitHub Repo](https://github.com)")
        st.markdown("[Portfolio](https://portfolio.com)")

    # Main Content
    
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <h1>Ask Chatbot!</h1>
        <p>Your personal AI assistant trained on your documents. Fast ⚡ | Accurate 🔍 | Cites Sources 📚</p>
    </div>
    """, unsafe_allow_html=True)

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display "What can this do" if chat is empty
    if not st.session_state.messages:
        st.markdown("### 🚀 What can this AI do?")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🧠 Answer Questions</h4>
                <p>Ask anything about your uploaded medical documents.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🔍 Summarize Docs</h4>
                <p>Get quick summaries of complex medical reports.</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>📚 Provide Sources</h4>
                <p>Every answer comes with citations and page numbers.</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

    # Chat History
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if 'sources' in message:
                with st.expander("📚 Source Documents"):
                    for i, doc in enumerate(message['sources']):
                        st.markdown(f"**Source {i+1}:**")
                        st.markdown(doc.page_content)
                        st.markdown(f"*Source: {doc.metadata.get('source', 'Unknown')} (Page: {doc.metadata.get('page', 'Unknown')})*")
                        st.divider()

    # Input Area
    prompt=st.chat_input("Ask a question about your documents...")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role':'user', 'content': prompt})

        CUSTOM_PROMPT_TEMPLATE = """
                Use the pieces of information provided in the context to answer user's question.
                If you dont know the answer, just say that you dont know, dont try to make up an answer. 
                Dont provide anything out of the given context

                
                Context: {context}
                Question: {question}
                
                Start the answer directly. No small talk please.
                """
        
        try: 
            vectorstore=get_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")

            # Note: Using the temperature from sidebar
            qa_chain = RetrievalQA.from_chain_type(
                llm=ChatGroq(
                    model_name="meta-llama/llama-4-maverick-17b-128e-instruct",  # free, fast Groq-hosted model
                    temperature=temperature, # Use sidebar temperature
                    groq_api_key=os.environ["GROQ_API_KEY"],
                ),
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={'k':3}),
                return_source_documents=True,
                chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
            )

            with st.spinner("Thinking..."):
                response=qa_chain.invoke({'query':prompt})

            result=response["result"]
            source_documents=response["source_documents"]
            
            with st.chat_message('assistant'):
                st.markdown(result)
                with st.expander("📚 Source Documents"):
                    for i, doc in enumerate(source_documents):
                        st.markdown(f"**Source {i+1}:**")
                        st.markdown(doc.page_content)
                        st.markdown(f"*Source: {doc.metadata.get('source', 'Unknown')} (Page: {doc.metadata.get('page', 'Unknown')})*")
                        st.divider()

            st.session_state.messages.append({'role':'assistant', 'content': result, 'sources': source_documents})

        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Footer
    st.markdown("""
    <div class="footer">
        <p>Powered by <strong>LangChain</strong> | <strong>Streamlit</strong> | <strong>Groq</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
