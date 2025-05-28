import os
import json
from qdrant_client import QdrantClient
from openai import AzureOpenAI
from langchain.embeddings.base import Embeddings

# === Configs ===
COLLECTION_NAME = "rag-pipeline"
TOP_K = 1

os.environ["AZURE_OPENAI_API_KEY"] = "b46942d9305c42d78df6078a465419ae"  
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzUxMDMxMzk5fQ.9vcCjGS78-nZ3_k3tVIlJ_mA7pYuHShGAuP80EICCCg"



# === Azure OpenAI Setup ===
endpoint = "https://qrizz-us.openai.azure.com"
deployment = "text-embedding-3-small"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_endpoint=endpoint,
    api_version=api_version
)

class AzureOpenAIEmbeddings(Embeddings):
    def __init__(self, client, deployment):
        self.client = client
        self.deployment = deployment

    def embed_documents(self, texts):
        response = self.client.embeddings.create(
            input=texts,
            model=self.deployment
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text):
        return self.embed_documents([text])[0]

embedder = AzureOpenAIEmbeddings(client, deployment)

# === Qdrant Client ===
qdrant = QdrantClient(
    url="https://2be815d0-8825-4538-aa70-5df6ac6ee017.eu-west-2-0.aws.cloud.qdrant.io:6333",
    api_key=os.getenv("QDRANT_API_KEY")
)

# === Function to Perform Retrieval ===
def retrieve_metadata(query: str):
    print(f"🔍 Searching for: {query}")
    query_vector = embedder.embed_query(query)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=TOP_K
    )

    if not results:
        print("❌ No match found.")
        return None

    top_result = results[0]
    payload = top_result.payload
    metadata_path = payload.get("metadata_path")

    print(f"✅ Top match: {payload.get('file_name')}")
    print(f"📄 Metadata path: {metadata_path}")

    return metadata_path


# === Example Usage ===
if __name__ == "__main__":
    query_input = input("Enter your search query: ")
    path = retrieve_metadata(query_input)

    if path:
        print("\n🧠 Use this metadata path for downstream processing:")
        print(path)

