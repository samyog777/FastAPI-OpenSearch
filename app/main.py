from fastapi import FastAPI, HTTPException, status
from app.services.opensearch_service import opensearch_service
from app.schemas.item import ItemCreate, ItemUpdate, Item
import uuid

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await opensearch_service.create_index()

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    item_id = str(uuid.uuid4())
    document = item.model_dump()
    response = await opensearch_service.create_document(document, item_id)
    
    if not response.get("result") == "created":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item"
        )
    
    return Item(id=item_id, **document)

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    document = await opensearch_service.get_document(item_id)
    if not document or not document.get("found"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return Item(id=item_id, **document["_source"])

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: ItemUpdate):
    # Check if item exists
    existing = await opensearch_service.get_document(item_id)
    if not existing or not existing.get("found"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Update only provided fields
    update_data = item.model_dump(exclude_unset=True)
    response = await opensearch_service.update_document(item_id, update_data)
    
    if not response.get("result") == "updated":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item"
        )
    
    # Return the updated item
    updated = await opensearch_service.get_document(item_id)
    return Item(id=item_id, **updated["_source"])

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    # Check if item exists
    existing = await opensearch_service.get_document(item_id)
    if not existing or not existing.get("found"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    response = await opensearch_service.delete_document(item_id)
    if not response.get("result") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item"
        )
    
    return None

@app.get("/items/", response_model=dict)
async def search_items(
    query: str = None,
    page: int = 1,
    size: int = 10
):
    # Calculating pagination offset
    from_ = (page - 1) * size

    # Building the search query
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
        # If no query is passed, return all items (used pagination)
        search_query = {
            "from": from_,
            "size": size,
            "query": {
                "match_all": {}
            }
        }

    response = await opensearch_service.search_documents(search_query)

    total_hits = response["hits"]["total"]["value"]
    hits = response["hits"]["hits"]

    items = [
        Item(id=hit["_id"], **hit["_source"])
        for hit in hits
    ]

    return {
        "items_returned": len(items),
        "total_items": total_hits,
        "items": items,
        "more_items_available": max(0, total_hits - (page * size))
    }
