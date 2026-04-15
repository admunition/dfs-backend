from fastapi import APIRouter, HTTPException
from app.controllers.example import (
    get_all_items,
    get_item_by_id,
    create_item,
    update_item,
    delete_item,
)
from app.schemas.example import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter()


@router.get("/", response_model=list[ItemResponse])
async def list_items():
    return await get_all_items()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    item = await get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemResponse, status_code=201)
async def create(payload: ItemCreate):
    return await create_item(payload)


@router.put("/{item_id}", response_model=ItemResponse)
async def update(item_id: str, payload: ItemUpdate):
    item = await update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{item_id}")
async def delete(item_id: str):
    deleted = await delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
