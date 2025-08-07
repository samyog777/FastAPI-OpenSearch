import uuid
from fastapi import APIRouter, HTTPException, status
from app.services.items import item_service
from app.schemas.item import ItemCreate, ItemUpdate, Item

router = APIRouter()

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    item_id = str(uuid.uuid4())
    document = item.model_dump()
    response = await item_service.create_document(document, item_id)

    if response.get("result") != "created":
        raise HTTPException(status_code=500, detail="Failed to create item")

    return Item(id=item_id, **document)


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: str):
    document = await item_service.get_document(item_id)
    if not document or not document.get("found"):
        raise HTTPException(status_code=404, detail="Item not found")

    return Item(id=item_id, **document["_source"])


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemUpdate):
    existing = await item_service.get_document(item_id)
    if not existing or not existing.get("found"):
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item.model_dump(exclude_unset=True)
    response = await item_service.update_document(item_id, update_data)

    if response.get("result") != "updated":
        raise HTTPException(status_code=500, detail="Failed to update item")

    updated = await item_service.get_document(item_id)
    return Item(id=item_id, **updated["_source"])


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    existing = await item_service.get_document(item_id)
    if not existing or not existing.get("found"):
        raise HTTPException(status_code=404, detail="Item not found")

    response = await item_service.delete_document(item_id)
    if response.get("result") != "deleted":
        raise HTTPException(status_code=500, detail="Failed to delete item")


@router.get("/", response_model=dict)
async def search_items(query: str = None, page: int = 1, size: int = 10):
    from_ = (page - 1) * size

    if query:
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "description"]
                }
            }
        }
    else:
        search_query = {
            "from": from_,
            "size": size,
            "query": {"match_all": {}}
        }

    response = await item_service.search_documents(search_query)
    total_hits = response["hits"]["total"]["value"]
    hits = response["hits"]["hits"]

    items = [Item(id=hit["_id"], **hit["_source"]) for hit in hits]

    return {
        "items_returned": len(items),
        "total_items": total_hits,
        "items": items,
        "more_items_available": max(0, total_hits - (page * size))
    }
