from rag_query_pinecone import query_documents

def test_rag():
    # Test questions
    test_questions = [
        "What are the key steps in the RAG process?",
        "How does the system handle document retrieval?",
        "What is the role of DPR in the system?"
    ]
    
    print("Testing RAG system with Pinecone...")
    print("-" * 50)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        try:
            answer = query_documents(question)
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_rag()
