import os
from opensearchpy import OpenSearch, exceptions
from dotenv import load_dotenv

load_dotenv()

class OpenSearchService:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[os.getenv("OPENSEARCH_HOST")],
            http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASSWORD")),
            use_ssl=True,
            verify_certs=os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true",
            ssl_show_warn=False
        )
        self.index_name = os.getenv("OPENSEARCH_INDEX", "items")

    async def create_index(self):
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "index": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    }
                },
                "mappings": {
                    "properties": {
                        "name": {"type": "text"},
                        "description": {"type": "text"},
                        "price": {"type": "float"},
                        "in_stock": {"type": "boolean"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=index_body)

    async def create_document(self, document: dict, id: str = None):
        return self.client.index(
            index=self.index_name,
            body=document,
            id=id,
            refresh=True
        )

    async def get_document(self, id: str):
        try:
            return self.client.get(
                index=self.index_name,
                id=id
            )
        except exceptions.NotFoundError:
            return None

    async def update_document(self, id: str, document: dict):
        return self.client.update(
            index=self.index_name,
            id=id,
            body={"doc": document},
            refresh=True
        )

    async def delete_document(self, id: str):
        return self.client.delete(
            index=self.index_name,
            id=id,
            refresh=True
        )

    async def search_documents(self, query: dict):
        return self.client.search(
            index=self.index_name,
            body=query
        )

opensearch_service = OpenSearchService()