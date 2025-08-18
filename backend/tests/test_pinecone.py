from backend.utils.vector_db import query_vector_db, health_check
from backend.utils.embedding import get_embedding


def main():
    print("=== Health Check ===")
    ok = health_check()
    print("Health:", ok)

    print("\n=== Query Test with Real Embedding ===")
    test_text = "DeFi insurance smart contracts" 
    embedding = get_embedding(test_text)

    try:
        matches = query_vector_db(embedding, top_k=3)
        print("Query success. Matches:")
        for m in matches:
            print(f"id={m.id}, score={m.score}")
    except Exception as e:
        print("Query failed:", e)


if __name__ == "__main__":
    main()
