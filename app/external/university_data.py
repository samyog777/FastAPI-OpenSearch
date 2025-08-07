from fastapi import APIRouter, Query
from app.services.university import university_service
import httpx
from fastapi import HTTPException
from app.schemas.university import SaveResult, University

router = APIRouter()


# ! comment out because it is used to test external API
# @router.get("/external-universities")
async def fetch_universities_from_api(country: str) -> list[dict]:
    url = f"http://universities.hipolabs.com/search?country={country}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch universities: {response.status_code}")

    return response.json()


async def save_university_to_opensearch(universities: list[dict]) -> int:
    save_count = 0

    for university in universities:
        if not university.get("domains"):
            continue

        doc_id = university["domains"][0]

        doc = {
            "web_pages": university.get("web_pages", []),
            "state_province": university.get("state_province"),
            "name": university.get("name"),
            "domains": university.get("domains", []),
            "country": university.get("country"),
            "alpha_two_code": university.get("alpha_two_code"),
        }

        existing = await university_service.get_document(doc_id)
        if existing:
            continue

        res = await university_service.create_document(doc, doc_id)

        if res.get("result") == "created":
            save_count += 1

    return save_count


# ! Comment out because its function is already used in /country save + fetch
# @router.post("/fetch-and-save-to-opensearch", response_model=SaveResult)
async def fetch_and_save_universities(country: str):
    try:
        universities = await fetch_universities_from_api(country)
        save_count = await save_university_to_opensearch(universities)
        return SaveResult(total_fetched=len(universities), total_saved=save_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
! The following code does these things:
   * 1. Search for the university per country in local database "OpenSearch"
   * 2. If the country's data is missing in local database, fetch from external API
   * 3. Save that fetched data and return using pagination
   * 4. If the country's name is not present in external API or the country's name is mistaken then,
   * 5. It returns the empty list
"""


@router.get("/{country}")
async def get_universities_by_country_or_fetch_external_and_save(
    country: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
):
    _from = (page - 1) * size

    # First search
    response = await university_service.search_documents(
        {"from": _from, "size": size, "query": {"match": {"country": country}}}
    )

    hits = response["hits"]["hits"]
    total_hits = response["hits"]["total"]["value"]
    universities = [University(id=hit["_id"], **hit["_source"]) for hit in hits]

    # If no data, fetch and save from external API
    if not universities:
        external_unis = await fetch_universities_from_api(country)
        await save_university_to_opensearch(external_unis)

        response = await university_service.search_documents(
            {"from": _from, "size": size, "query": {"match": {"country": country}}}
        )

        hits = response["hits"]["hits"]
        total_hits = response["hits"]["total"]["value"]
        universities = [University(id=hit["_id"], **hit["_source"]) for hit in hits]

    return {
        "page": page,
        "size": size,
        "total": total_hits,
        "data": universities,
        "remaining": max(0, total_hits - (page * size)),
    }
