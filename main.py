import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Listing, Offer

app = FastAPI(title="CardTrader API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "CardTrader API is running"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Helper to convert ObjectId to string for JSON
class ListingOut(BaseModel):
    id: str
    title: str
    game: str
    set_name: Optional[str] = None
    year: Optional[int] = None
    card_number: Optional[str] = None
    condition: Optional[str] = None
    grade: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    for_trade: bool
    owner_name: Optional[str] = None
    contact: Optional[str] = None
    notes: Optional[str] = None


@app.post("/api/listings", response_model=dict)
def create_listing(payload: Listing):
    try:
        listing_id = create_document("listing", payload)
        return {"id": listing_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/listings", response_model=List[ListingOut])
def list_listings(q: Optional[str] = None, game: Optional[str] = None):
    try:
        filter_dict = {}
        if game:
            filter_dict["game"] = game
        if q:
            # simple text search on few fields (case-insensitive)
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"set_name": {"$regex": q, "$options": "i"}},
                {"notes": {"$regex": q, "$options": "i"}},
            ]
        docs = get_documents("listing", filter_dict)
        results = []
        for d in docs:
            results.append(ListingOut(
                id=str(d.get("_id")),
                title=d.get("title"),
                game=d.get("game"),
                set_name=d.get("set_name"),
                year=d.get("year"),
                card_number=d.get("card_number"),
                condition=d.get("condition"),
                grade=d.get("grade"),
                image_url=d.get("image_url"),
                price=d.get("price"),
                for_trade=d.get("for_trade", True),
                owner_name=d.get("owner_name"),
                contact=d.get("contact"),
                notes=d.get("notes"),
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class OfferCreate(Offer):
    pass

class OfferOut(BaseModel):
    id: str
    listing_id: str
    offer_type: str
    message: Optional[str] = None
    offered_value: Optional[float] = None
    offered_card: Optional[str] = None
    buyer_name: Optional[str] = None
    contact: Optional[str] = None
    status: str


@app.post("/api/offers", response_model=dict)
def create_offer(payload: OfferCreate):
    # Validate listing existence
    try:
        listing_oid = ObjectId(payload.listing_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid listing_id")

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    listing = db["listing"].find_one({"_id": listing_oid})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    try:
        offer_id = create_document("offer", payload)
        return {"id": offer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/offers", response_model=List[OfferOut])
def list_offers(listing_id: Optional[str] = None):
    try:
        filter_dict = {}
        if listing_id:
            filter_dict["listing_id"] = listing_id
        docs = get_documents("offer", filter_dict)
        results = []
        for d in docs:
            results.append(OfferOut(
                id=str(d.get("_id")),
                listing_id=d.get("listing_id"),
                offer_type=d.get("offer_type"),
                message=d.get("message"),
                offered_value=d.get("offered_value"),
                offered_card=d.get("offered_card"),
                buyer_name=d.get("buyer_name"),
                contact=d.get("contact"),
                status=d.get("status", "pending"),
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
