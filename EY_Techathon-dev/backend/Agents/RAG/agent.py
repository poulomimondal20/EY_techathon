import os
import re
import google.generativeai as genai
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

class RAGSystem:
    def __init__(self, api_key=None):
        """Initialize the RAG system with configurations."""
        # Load environment variables
        load_dotenv()
        
        # Configure Google Generative AI API key
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorstore = None

    def build_knowledge_base(self, file_paths):
        """Build a vector store from PDF documents using langchain components."""
        all_splits = []
        for file_path in file_paths:
            if file_path.lower().endswith('.pdf'):
                print(f"Processing {file_path}...")
                try:
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                        chunk_size=300, 
                        chunk_overlap=50
                    )
                    splits = text_splitter.split_documents(docs)
                    all_splits.extend(splits)
                except Exception as e:
                    print(f"Could not process {file_path}: {e}")
            else:
                print(f"Unsupported file type for {file_path}")
        
        if all_splits:
            embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vectorstore = Chroma.from_documents(documents=all_splits, embedding=embedding_model)
            return True
        return False

    def retrieve(self, query, top_k=5):
        """Retrieve the top_k most relevant documents from the vectorstore."""
        if not self.vectorstore:
            raise ValueError("Knowledge base not built. Call build_knowledge_base first.")
            
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        results = retriever.get_relevant_documents(query)
        return results

    def generate_answer(self, question, retrieved_docs, prompt_template):
        """Generate an answer using retrieved documents and a prompt template."""
        # Format retrieved documents into context
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        formatted_prompt = prompt_template.format(context=context, question=question)
        
        # Generate response using the LLM
        response = self.llm.invoke(formatted_prompt)
        return response

    def query(self, question, prompt_template=None):
        """Process a question through the full RAG pipeline."""
        if not prompt_template:
            prompt_template = """Context: {context}\n\nQuestion: {question}\nAnswer:"""
            
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question)
        
        # Print retrieved context information
        print("Retrieved Context: ")
        for item in retrieved_docs:
            source = item.metadata.get('source', 'Unknown source')
            page = item.metadata.get('page', 'Unknown page')
            print(f"File: {source} - Page {page}")
        
        # Generate and return answer
        response = self.generate_answer(question, retrieved_docs, prompt_template)
        return response.content

def main():
    # Initialize the RAG system
    rag = RAGSystem()
    
    # Define file paths
    file_paths = ["Temp/2401.06167v1.pdf"]  # Update with your PDF path
    
    # Build the knowledge base
    if rag.build_knowledge_base(file_paths):
        while True:
            # Get user question
            question = input("\nEnter your question (or 'quit' to exit): ")
            if question.lower() == 'quit':
                break
                
            # Get answer
            response = rag.query(question)
            print("\nAnswer:\n", response)
            print("Answer type:", type(response))
    else:
        print("Failed to build knowledge base. Please check your PDF files.")

if __name__ == "__main__":
    main()