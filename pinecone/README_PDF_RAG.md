# PDF RAG System with Pinecone

This system allows you to upload PDF content to Pinecone vector database and ask questions about the content.

## Files Overview

1. **main.py** - Original Pinecone example with static records
2. **main_v1.py** - Interactive PDF RAG system
3. **demo_pdf_rag.py** - Non-interactive demo version
4. **create_sample_pdf.py** - Creates a sample PDF for testing
5. **temp.pdf** - Sample PDF file created for testing

## Setup Instructions

### 1. Install Required Packages
The following packages are already installed in your virtual environment:
- `python-dotenv` - For loading environment variables
- `pypdf` - For reading PDF files
- `reportlab` - For creating PDF files (used in demo)
- `pinecone` - Pinecone client

### 2. Environment Configuration
Make sure your `.env` file contains:
```
PINECONE_API_KEY=your_actual_api_key_here
```

### 3. Running the System

#### Option A: Interactive Mode (main_v1.py)
```bash
cd pinecone
& "../venv/Scripts/python.exe" main_v1.py
```
This will:
- Extract text from temp.pdf
- Create chunks and upload to Pinecone
- Start an interactive Q&A session
- Type your questions and get answers based on PDF content
- Type 'quit' to exit

#### Option B: Demo Mode (demo_pdf_rag.py)
```bash
cd pinecone
& "../venv/Scripts/python.exe" demo_pdf_rag.py
```
This will run predefined demo queries and show results.

## How It Works

### 1. PDF Processing
- Extracts text from PDF using pypdf library
- Splits text into chunks (1000 characters with 100 character overlap)
- Creates metadata for each chunk

### 2. Vector Database Setup
- Creates a Pinecone index with llama-text-embed-v2 embeddings
- Uploads text chunks as vectors to Pinecone
- Each chunk becomes a searchable record

### 3. Question Answering
- Takes user queries
- Searches vector database for most relevant chunks
- Returns top matches with similarity scores

## Key Features

- **Automatic PDF text extraction**
- **Intelligent text chunking** with overlap to preserve context
- **Vector similarity search** using Pinecone
- **Interactive Q&A interface**
- **Relevance scoring** for search results

## Customization Options

### Modify Chunk Size
In the `chunk_text()` function:
```python
chunk_size = 1000  # Adjust chunk size
overlap = 100      # Adjust overlap
```

### Change Search Parameters
In the `search_pdf_content()` function:
```python
top_k = 5  # Number of results to return
```

### Use Different PDF
Replace `temp.pdf` with your own PDF file in the pinecone folder.

## Example Usage

After running the system, you can ask questions like:
- "What is artificial intelligence?"
- "Tell me about machine learning"
- "What are the applications mentioned?"
- "Explain deep learning concepts"

The system will find the most relevant sections from your PDF and display them with similarity scores.

## Troubleshooting

1. **PDF not found**: Make sure temp.pdf exists in the pinecone folder
2. **API key issues**: Check your .env file has the correct PINECONE_API_KEY
3. **Index creation fails**: Wait a few moments between operations, Pinecone needs time to process
4. **No results**: Try different query terms or check if PDF content was properly extracted

## Next Steps

You can extend this system by:
- Adding support for multiple PDF files
- Implementing better text preprocessing
- Adding metadata filtering
- Creating a web interface
- Adding conversation memory
