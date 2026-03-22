from app.rag.vector_store import VectorStore


class Retriever:
    def __init__(self):
        self.store = VectorStore()

    def retrieve(self, query, top_k=3):
        results = self.store.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        return results["metadatas"][0]