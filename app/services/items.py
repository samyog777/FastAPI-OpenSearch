from app.services.base_opensearch import BaseOpenSearchService

class ItemService(BaseOpenSearchService):
    def __init__(self):
        mappings = {
            "name": {"type": "text"},
            "description": {"type": "text"},
            "price": {"type": "float"},
            "in_stock": {"type": "boolean"}
        }
        super().__init__(index_name="items", mappings=mappings)

item_service = ItemService()
