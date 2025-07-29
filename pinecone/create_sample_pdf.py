# Script to create a sample PDF for testing
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf():
    """Create a sample PDF file for testing"""
    filename = "temp.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add content to the PDF
    content = [
        "Sample PDF Document for RAG Testing",
        "",
        "Chapter 1: Introduction to Artificial Intelligence",
        "Artificial Intelligence (AI) is a branch of computer science that aims to create",
        "intelligent machines that can perform tasks that typically require human intelligence.",
        "These tasks include learning, reasoning, problem-solving, perception, and language understanding.",
        "",
        "Chapter 2: Machine Learning Fundamentals",
        "Machine learning is a subset of AI that provides systems the ability to automatically",
        "learn and improve from experience without being explicitly programmed.",
        "There are three main types of machine learning:",
        "1. Supervised Learning - Learning with labeled data",
        "2. Unsupervised Learning - Finding patterns in unlabeled data", 
        "3. Reinforcement Learning - Learning through interaction with environment",
        "",
        "Chapter 3: Deep Learning",
        "Deep learning is a subset of machine learning based on artificial neural networks.",
        "It has been particularly successful in areas such as:",
        "- Computer Vision",
        "- Natural Language Processing", 
        "- Speech Recognition",
        "- Autonomous Driving",
        "",
        "Chapter 4: Applications of AI",
        "AI has numerous applications across various industries:",
        "Healthcare: Medical diagnosis, drug discovery, personalized treatment",
        "Finance: Fraud detection, algorithmic trading, risk assessment",
        "Technology: Search engines, recommendation systems, virtual assistants",
        "Transportation: Autonomous vehicles, route optimization, traffic management",
        "",
        "Conclusion:",
        "The future of AI holds great promise for solving complex problems and",
        "improving human life across multiple domains."
    ]
    
    y = 750  # Starting y position
    for line in content:
        c.drawString(50, y, line)
        y -= 20
        if y < 50:  # Start new page if needed
            c.showPage()
            y = 750
    
    c.save()
    print(f"Sample PDF '{filename}' created successfully!")

if __name__ == "__main__":
    create_sample_pdf()
