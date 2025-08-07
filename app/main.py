from fastapi import FastAPI
from app.services.items import item_service
from app.services.university import university_service
from app.routers.items import router as items_router
from app.external.university_data import router as external_university_router
from app.routers.universities import router as universities_router

app = FastAPI()

app.include_router(items_router, prefix="/items", tags=["Items"])
app.include_router(universities_router, prefix="/universities", tags=["Universities"])
app.include_router(
    external_university_router,
    prefix="/external-universities",
    tags=["External Universities"],
)


@app.on_event("startup")
async def startup_event():
    await item_service.create_index()
    await university_service.create_index()
