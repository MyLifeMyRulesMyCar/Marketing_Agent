import os
import yaml
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

import pandas as pd


# ----------------------------
# LOAD CONFIG
# ----------------------------
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

DATA_PATH = config["data_path"]
DB_PATH = config["db_path"]


# ----------------------------
# LOAD DOCUMENTS
# ----------------------------
def load_documents(folder_path):
    documents = []

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

        elif file.endswith(".docx"):
            loader = UnstructuredWordDocumentLoader(file_path)
            documents.extend(loader.load())

        elif file.endswith(".txt"):
            loader = TextLoader(file_path)
            documents.extend(loader.load())

        elif file.endswith(".xlsx"):
            df = pd.read_excel(file_path)

            for i, row in df.iterrows():
                text = " | ".join([str(v) for v in row.values])
                documents.append({
                    "page_content": text,
                    "metadata": {"source": file, "row": i}
                })

    return documents


# ----------------------------
# SPLIT TEXT
# ----------------------------
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"]
    )

    texts = []

    for doc in documents:
        if isinstance(doc, dict):
            texts.extend(text_splitter.create_documents(
                [doc["page_content"]],
                metadatas=[doc["metadata"]]
            ))
        else:
            texts.extend(text_splitter.split_documents([doc]))

    return texts


# ----------------------------
# CREATE VECTOR DB
# ----------------------------
def create_vector_db(texts):
    embeddings = HuggingFaceEmbeddings(
        model_name=config["embedding_model"]
    )

    db = FAISS.from_documents(texts, embeddings)

    os.makedirs(DB_PATH, exist_ok=True)
    db.save_local(DB_PATH)

    print("✅ Vector DB created successfully!")


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    print("📥 Loading documents...")
    docs = load_documents(DATA_PATH)

    print(f"📄 Loaded {len(docs)} documents")

    print("✂️ Splitting documents...")
    texts = split_documents(docs)

    print(f"🧩 Created {len(texts)} chunks")

    print("🧠 Creating vector DB...")
    create_vector_db(texts)
