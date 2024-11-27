from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

pc = Pinecone()
print("Current indexes:", pc.list_indexes().names())
