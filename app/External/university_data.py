from fastapi import APIRouter
from app.services.university import university_service
import httpx
from fastapi import HTTPException
from app.schemas.university import SaveResult

router = APIRouter()

@router.get("/external-universities")
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
            "alpha_two_code": university.get("alpha_two_code")
        }

        existing = await university_service.get_document(doc_id)
        if existing:
            continue

        res = await university_service.create_document(doc, doc_id)

        if res.get("result") == "created":
            save_count += 1
    
    return save_count

@router.post("/fetch-and-save-to-opensearch", response_model=SaveResult)
async def fetch_and_save_universities(country: str):
    try:
        universities = await fetch_universities_from_api(country)
        save_count = await save_university_to_opensearch(universities)
        return SaveResult(total_fetched=len(universities), total_saved=save_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

