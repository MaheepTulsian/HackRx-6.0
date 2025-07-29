# Fixed version with batch processing for large PDFs
import os
import time
import requests
import io
from dotenv import load_dotenv
from pinecone import Pinecone
from pypdf import PdfReader
from typing import List

# Load environment variables from .env file
load_dotenv()

# Initialize a Pinecone client with your API key from environment variable
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """Extract text from PDF URL without downloading to disk"""
    try:
        print(f"Fetching PDF from URL: {pdf_url}")
        
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Download PDF content into memory
        response = requests.get(pdf_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Downloaded {len(response.content)} bytes")
        
        # Check if the content is actually a PDF
        if response.content[:4] != b'%PDF':
            print("Warning: Downloaded content doesn't appear to be a PDF")
            return ""
        
        # Create a BytesIO object from the response content
        pdf_bytes = io.BytesIO(response.content)
        
        # Read PDF from memory
        reader = PdfReader(pdf_bytes)
        text = ""
        print(f"PDF has {len(reader.pages)} pages")
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            except Exception as e:
                print(f"Error extracting text from page {page_num + 1}: {e}")
                continue
        
        print(f"Successfully extracted text from PDF URL")
        return text
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from URL: {e}")
        return ""
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

def create_records_from_pdf_url(pdf_url: str) -> List[dict]:
    """Convert PDF URL content to Pinecone records"""
    print(f"Processing PDF from URL: {pdf_url}")
    text = extract_text_from_pdf_url(pdf_url)
    
    if not text:
        print("No text extracted from PDF URL")
        return []
    
    print(f"Extracted {len(text)} characters from PDF")
    
    # Split text into chunks
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks")
    
    # Create records
    records = []
    source_name = pdf_url.split('/')[-1]
    
    for i, chunk in enumerate(chunks):
        record = {
            "_id": f"url_pdf_chunk_{i+1}",
            "chunk_text": chunk,
            "source": source_name,
            "source_url": pdf_url,
            "chunk_number": i+1
        }
        records.append(record)
    
    return records

def upload_records_in_batches(index, records: List[dict], namespace: str, batch_size: int = 90):
    """Upload records to Pinecone in batches to avoid size limits"""
    total_records = len(records)
    print(f"Uploading {total_records} records in batches of {batch_size}...")
    
    for i in range(0, total_records, batch_size):
        batch = records[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total_records + batch_size - 1) // batch_size
        
        print(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} records)...")
        
        try:
            index.upsert_records(namespace, batch)
            print(f"✅ Batch {batch_num} uploaded successfully")
            
            # Small delay between batches to avoid rate limits
            if batch_num < total_batches:
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error uploading batch {batch_num}: {e}")
            continue
    
    print(f"✅ All batches uploaded successfully!")

def search_pdf_content(query: str, index, namespace: str = "pdf-url-namespace", top_k: int = 5):
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
            print(f"   Source: {hit['fields']['source']}")
            print(f"   Text: {hit['fields']['chunk_text'][:300]}...")
    else:
        print("No results found")
    
    return results

def main():
    # HackRx PDF URL
    pdf_url = "https://hackrx.in/policies/BAJHLIP23020V012223.pdf"
    
    print("PDF URL RAG System - Fixed Version")
    print("=" * 50)
    print(f"Processing PDF from: {pdf_url}")
    
    # Create a dense index with integrated embedding
    index_name = "hackrx-pdf-fixed"
    
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
    
    # Create records from PDF URL
    records = create_records_from_pdf_url(pdf_url)
    
    if not records:
        print("No records created from PDF URL")
        return
    
    # Target the index
    dense_index = pc.Index(index_name)
    
    # Upload records in batches (Pinecone limit is ~96 records per batch)
    upload_records_in_batches(dense_index, records, "pdf-url-namespace", batch_size=90)
    
    # Wait for upsert to complete
    print("Waiting for final upsert to complete...")
    time.sleep(5)
    
    # View stats for the index
    stats = dense_index.describe_index_stats()
    print(f"\nIndex stats: {stats}")
    
    # Demo some queries
    demo_queries = [
        "What is this document about?",
        "What are the key policies mentioned?",
        "Tell me about coverage details",
        "What are the terms and conditions?",
        "What is the premium amount?"
    ]
    
    print("\n" + "="*60)
    print("DEMO QUERIES - PDF URL RAG System")
    print("="*60)
    
    for query in demo_queries:
        search_pdf_content(query, dense_index)
        print("\n" + "-"*50)
    
    # Interactive Q&A loop
    print("\n" + "="*50)
    print("Interactive Mode - Ask your own questions!")
    print("Type 'quit' or 'exit' to stop.")
    print("="*50)
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            print("Please enter a question.")
            continue
        
        # Search and display results
        search_pdf_content(query, dense_index)

if __name__ == "__main__":
    main()
