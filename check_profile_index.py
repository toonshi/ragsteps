from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()

pc = Pinecone()
index = pc.Index("profiles")
print("Profile index details:", index.describe_index_stats())
