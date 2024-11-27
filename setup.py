from setuptools import setup, find_packages

setup(
    name="ragsteps",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pinecone-client",
        "sentence-transformers",
        "python-dotenv",
        "langchain",
        "langchain_community",
        "langchain_openai",
        "chromadb",
        "transformers",
        "torch",
        "PyPDF2"
    ],
)
