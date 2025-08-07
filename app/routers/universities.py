import uuid
from fastapi import APIRouter, HTTPException, status, Query

# from app.external.university_data import fetch_universities_from_api
from app.services.university import university_service
from app.schemas.university import UniversityCreate, UniversityUpdate, University
# from app.external.university_data import (
#     fetch_universities_from_api,
#     save_university_to_opensearch,
# )

router = APIRouter()


@router.post("/", response_model=University, status_code=status.HTTP_201_CREATED)
async def create_university(university: UniversityCreate):
    university_id = str(uuid.uuid4())
    document = university.model_dump()
    response = await university_service.create_document(document, university_id)

    if response.get("result") != "created":
        raise HTTPException(status_code=500, detail="Failed to create university")

    return University(id=university_id, **document)


# ! Below code is already being used in external/university_data.py

# @router.get("/{country}")
# async def get_universities_by_country_or_fetch_external(
#     country: str,
#     page: int = Query(1, ge=1),
#     size: int = Query(10, ge=1),
# ):
#     _from = (page - 1) * size

#     # First search
#     response = await university_service.search_documents(
#         {"from": _from, "size": size, "query": {"match": {"country": country}}}
#     )

#     hits = response["hits"]["hits"]
#     total_hits = response["hits"]["total"]["value"]
#     universities = [University(id=hit["_id"], **hit["_source"]) for hit in hits]

#     # If no data, fetch and save from external API
#     if not universities:
#         external_unis = await fetch_universities_from_api(country)
#         await save_university_to_opensearch(external_unis)

#         # Re-query
#         response = await university_service.search_documents(
#             {"from": _from, "size": size, "query": {"match": {"country": country}}}
#         )

#         hits = response["hits"]["hits"]
#         total_hits = response["hits"]["total"]["value"]
#         universities = [University(id=hit["_id"], **hit["_source"]) for hit in hits]

#     return {
#         "page": page,
#         "size": size,
#         "total": total_hits,
#         "data": universities,
#         "remaining": max(0, total_hits - (page * size)),
#     }


@router.get("/{university_id}", response_model=University)
async def read_university(university_id: str):
    document = await university_service.get_document(university_id)
    if not document or not document.get("found"):
        raise HTTPException(status_code=404, detail="University not found")

    return University(id=university_id, **document["_source"])


@router.put("/{university_id}", response_model=University)
async def update_university(university_id: str, university: UniversityUpdate):
    existing = await university_service.get_document(university_id)
    if not existing or not existing.get("found"):
        raise HTTPException(status_code=404, detail="University not found")

    update_data = university.model_dump(exclude_unset=True)
    response = await university_service.update_document(university_id, update_data)

    if response.get("result") != "updated":
        raise HTTPException(status_code=500, detail="Failed to update university")

    updated = await university_service.get_document(university_id)
    return University(id=university_id, **updated["_source"])


@router.delete("/{university_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university(university_id: str):
    existing = await university_service.get_document(university_id)
    if not existing or not existing.get("found"):
        raise HTTPException(status_code=404, detail="University not found")

    response = await university_service.delete_document(university_id)
    if response.get("result") != "deleted":
        raise HTTPException(status_code=500, detail="Failed to delete university")


@router.get("/", response_model=dict)
async def search_universities(query: str = None, page: int = 1, size: int = 10):
    try:
        from_ = (page - 1) * size

        if query:
            search_query = {
                "from": from_,
                "size": size,
                "query": {
                    "multi_match": {"query": query, "fields": ["name", "description"]}
                },
            }
        else:
            search_query = {"from": from_, "size": size, "query": {"match_all": {}}}

        response = await university_service.search_documents(search_query)
        total_hits = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]

        universities = [University(id=hit["_id"], **hit["_source"]) for hit in hits]

        return {
            "universities_returned": len(universities),
            "total_universities": total_hits,
            "universities": universities,
            "more_universities_available": max(0, total_hits - (page * size)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
