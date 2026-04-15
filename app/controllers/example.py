from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db
from app.schemas.example import ItemCreate, ItemUpdate

COLLECTION = "items"


def _format(item: dict) -> dict:
    item["id"] = str(item.pop("_id"))
    return item


async def get_all_items():
    db = get_db()
    items = await db[COLLECTION].find().to_list(length=100)
    return [_format(i) for i in items]


async def get_item_by_id(item_id: str):
    db = get_db()
    item = await db[COLLECTION].find_one({"_id": ObjectId(item_id)})
    return _format(item) if item else None


async def create_item(payload: ItemCreate):
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = {**payload.model_dump(), "created_at": now, "updated_at": now}
    result = await db[COLLECTION].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _format(doc)


async def update_item(item_id: str, payload: ItemUpdate):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    updates["updated_at"] = datetime.now(timezone.utc)
    result = await db[COLLECTION].find_one_and_update(
        {"_id": ObjectId(item_id)},
        {"$set": updates},
        return_document=True,
    )
    return _format(result) if result else None


async def delete_item(item_id: str):
    db = get_db()
    result = await db[COLLECTION].delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count > 0
