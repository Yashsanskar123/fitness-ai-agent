import chromadb
from app.rag.embedder import Embedder
import json


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("exercises")
        self.embedder = Embedder()

    def load_data(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)

        documents = []
        metadatas = []
        ids = []

        for i, item in enumerate(data):
            text = f"{item['name']} {item['muscle_group']} {item['description']}"
            documents.append(text)
            metadatas.append(item)
            ids.append(str(i))

        embeddings = self.embedder.embed(documents)

        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print("✅ Data loaded into vector DB")