"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal

# Example schemas (you can keep these for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App schemas

class Listing(BaseModel):
    """
    Marketplace listings for cards
    Collection name: "listing"
    """
    title: str = Field(..., description="Card title, e.g., 1999 Charizard Holo or 2019 Prizm Zion RC")
    game: Literal["pokemon", "sports"] = Field(..., description="Card category")
    set_name: Optional[str] = Field(None, description="Set/Brand, e.g., Base Set, Prizm, Topps")
    year: Optional[int] = Field(None, description="Year of release")
    card_number: Optional[str] = Field(None, description="Card number in the set")
    condition: Optional[str] = Field(None, description="Raw condition, e.g., NM, LP, HP")
    grade: Optional[str] = Field(None, description="Graded label, e.g., PSA 10, BGS 9.5")
    image_url: Optional[str] = Field(None, description="Image URL")
    price: Optional[float] = Field(None, ge=0, description="Asking price if selling")
    for_trade: bool = Field(True, description="Available for trade")
    owner_name: Optional[str] = Field(None, description="Seller/Trader name")
    contact: Optional[str] = Field(None, description="Contact info, e.g., email or handle")
    notes: Optional[str] = Field(None, description="Extra details")

class Offer(BaseModel):
    """
    Trade or purchase offers on listings
    Collection name: "offer"
    """
    listing_id: str = Field(..., description="Target listing _id as string")
    offer_type: Literal["trade", "buy"] = Field(..., description="Type of offer")
    message: Optional[str] = Field(None, description="Message to owner")
    offered_value: Optional[float] = Field(None, ge=0, description="Dollar offer for buy or trade valuation")
    offered_card: Optional[str] = Field(None, description="If trade, describe your card(s)")
    buyer_name: Optional[str] = Field(None, description="Offeror name")
    contact: Optional[str] = Field(None, description="Contact info")
    status: Literal["pending", "accepted", "declined"] = Field("pending", description="Offer status")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
