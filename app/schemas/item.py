from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None


class Item(ItemCreate):
    id: str

    class Config:
        from_attributes = True
