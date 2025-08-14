from sentence_transformers import SentenceTransformer

# Load MiniLM model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """Generate embedding vector for a text query."""
    return model.encode(text).tolist()
