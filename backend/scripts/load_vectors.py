"""
This script loads vectors from a JSONL file and uploads them to a Pinecone index.
It uses the SentenceTransformer model to encode text into vectors.
"""


import os
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from backend.config.settings import settings


# Initialize Pinecone client
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Connect to existing index
index = pc.Index(settings.PINECONE_INDEX)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load queries from JSONL file
jsonl_file = "backend/vector_db_queries.jsonl" 
with open(jsonl_file, "r") as f:
    data = [json.loads(line) for line in f]

print(f"ℹ️ Loaded {len(data)} queries from {jsonl_file}")

# Prepare vectors
vectors = []
for item in tqdm(data, desc="Encoding queries"):
    embedding = model.encode(item["text"]).tolist()
    vectors.append((
        item["id"],
        embedding,
        item["metadata"]
    ))

# Upsert in batches
batch_size = 100
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.upsert(vectors=batch)

print(f"✅ Uploaded {len(vectors)} vectors to Pinecone index '{settings.PINECONE_INDEX}'")
