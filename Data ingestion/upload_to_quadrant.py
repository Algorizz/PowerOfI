import os
import json
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from openai import AzureOpenAI
from langchain.embeddings.base import Embeddings

os.environ["AZURE_OPENAI_API_KEY"] = "b46942d9305c42d78df6078a465419ae"  
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-12-01-preview"
os.environ["QDRANT_API_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzUxMDMxMzk5fQ.9vcCjGS78-nZ3_k3tVIlJ_mA7pYuHShGAuP80EICCCg"


# === Azure OpenAI Embedding Setup ===
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

embedding_model = AzureOpenAIEmbeddings(client, deployment)

# === Qdrant Cloud Config ===
qdrant = QdrantClient(
    url="https://2be815d0-8825-4538-aa70-5df6ac6ee017.eu-west-2-0.aws.cloud.qdrant.io:6333", 
    api_key=os.getenv("QDRANT_API_KEY")
)

collection_name = "rag-pipeline"

# === Ensure Collection Exists ===
if not qdrant.collection_exists(collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

# === Load Payloads and Upload ===
payload_file = "qdrant_payloads.jsonl"

with open(payload_file, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line.strip())
        summary = item["summary"]
        point_id = item["id"]

        # Generate Azure OpenAI embedding
        embedding = embedding_model.embed_query(summary)

        payload = {
            "summary": summary,
            "metadata_path": item["metadata_path"],
            "file_name": item["file_name"]
        }

        qdrant.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        print(f"✅ Uploaded: {point_id}")

print("🎉 All payloads uploaded to Qdrant collection 'rag-pipeline'.")
