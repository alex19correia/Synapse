from src.services.qdrant_service import QdrantService
from src.config.settings import settings

def test_collection_creation():
    qdrant = QdrantService()
    collection_name = settings.QDRANT_COLLECTION
    if qdrant.create_collection(collection_name, vector_size=768):
        print(f"Collection '{collection_name}' created successfully!")
    else:
        print(f"Failed to create collection '{collection_name}'")

if __name__ == "__main__":
    test_collection_creation() 