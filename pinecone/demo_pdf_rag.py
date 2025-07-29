# Non-interactive version for demonstration
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from pypdf import PdfReader
from typing import List

# Load environment variables from .env file
load_dotenv()

# Initialize a Pinecone client with your API key from environment variable
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        print(f"PDF has {len(reader.pages)} pages")
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                chunk = text[start:break_point + 1]
                end = break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return [chunk for chunk in chunks if chunk]

def create_records_from_pdf(pdf_path: str) -> List[dict]:
    """Convert PDF content to Pinecone records"""
    print(f"Extracting text from PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("No text extracted from PDF")
        return []
    
    print(f"Extracted {len(text)} characters from PDF")
    
    # Split text into chunks
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")
    
    # Create records
    records = []
    for i, chunk in enumerate(chunks):
        record = {
            "_id": f"pdf_chunk_{i+1}",
            "chunk_text": chunk,
            "source": "temp.pdf",
            "chunk_number": i+1
        }
        records.append(record)
    
    return records

def search_pdf_content(query: str, index, namespace: str = "pdf-namespace", top_k: int = 3):
    """Search PDF content based on query"""
    print(f"\nSearching for: '{query}'")
    
    # Search the dense index
    results = index.search(
        namespace=namespace,
        query={
            "top_k": top_k,
            "inputs": {
                'text': query
            }
        }
    )
    
    print("\n=== Search Results ===")
    if 'result' in results and 'hits' in results['result']:
        for i, hit in enumerate(results['result']['hits'], 1):
            print(f"\n{i}. Score: {round(hit['_score'], 3)}")
            print(f"   Chunk: {hit['_id']}")
            print(f"   Text: {hit['fields']['chunk_text'][:300]}...")
    else:
        print("No results found")
    
    return results

def main():
    # PDF file path
    pdf_path = "temp.pdf"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"PDF file '{pdf_path}' not found in the current directory")
        return
    
    # Create a dense index with integrated embedding
    index_name = "pdf-demo-index"
    
    # Delete existing index if it exists (for fresh start)
    if pc.has_index(index_name):
        print(f"Deleting existing index: {index_name}")
        pc.delete_index(index_name)
        time.sleep(5)
    
    print(f"Creating new index: {index_name}")
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "chunk_text"}
        }
    )
    
    # Wait for index to be ready
    print("Waiting for index to be ready...")
    time.sleep(10)
    
    # Create records from PDF
    records = create_records_from_pdf(pdf_path)
    
    if not records:
        print("No records created from PDF")
        return
    
    # Target the index
    dense_index = pc.Index(index_name)
    
    # Upsert the records into a namespace
    print(f"Uploading {len(records)} records to Pinecone...")
    dense_index.upsert_records("pdf-namespace", records)
    
    # Wait for upsert to complete
    print("Waiting for upsert to complete...")
    time.sleep(10)
    
    # View stats for the index
    stats = dense_index.describe_index_stats()
    print(f"\nIndex stats: {stats}")
    
    # Demo queries
    demo_queries = [
        "What is Artificial Intelligence?",
        "Tell me about machine learning types",
        "What are the applications of AI?",
        "Explain deep learning"
    ]
    
    print("\n" + "="*60)
    print("DEMO: PDF Q&A System")
    print("="*60)
    
    for query in demo_queries:
        search_pdf_content(query, dense_index)
        print("\n" + "-"*50)

if __name__ == "__main__":
    main()
