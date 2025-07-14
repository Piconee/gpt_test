from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel
import requests
import os

app = FastAPI()

DMS_BASE_URL = "https://alpin-dev.d-velop.cloud/dms"  # Replace with real base URL
BEARER_TOKEN = "clz/cKSKWVF5NXa7poTS9RiN5S4QCGhjGxo0fE1QiB66qlfk1pGk3Pl5HFGT5y5IyW8c9jAMh7NefRWnFrT6FKLB3I06jTAE397KcEyPCnw=&_z_A0V5ayCTcDeHVN_zAEnmxEkZeE6im4OH05NlT0dh1poy0CbcKF_U1dq8-455l2Y3q4Sp-150HTIRGLRb_KTuaV5g0qQZW"  # Replace with your actual token

class SearchResultItem(BaseModel):
    id: str
    title: Optional[str] = None
    categories: List[str]
    properties: dict

@app.get("/search", response_model=List[SearchResultItem])
def search_documents(
    repository_id: str,
    query: Optional[str] = None,
    source_id: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    from_date: Optional[str] = None,  # Format: YYYY-MM-DD
    to_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    # Build query params
    params = {
        "searchFulltext": query,
        "mappingSourceId": source_id,
        "page": page,
        "pageSize": page_size
    }

    # Optional sourceProperties filtering (example structure)
    if tags:
        params["sourceproperties"] = {
            "tags": tags  # Only if this is a valid mapped property
        }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    dms_url = f"{DMS_BASE_URL}/r/{repository_id}/srm"

    response = requests.get(dms_url, headers=headers, params=params)

    if not response.ok:
        return [{"id": "error", "title": "DMS Error", "categories": [], "properties": {"reason": response.text}}]

    data = response.json()
    items = []

    for item in data.get("items", []):
        items.append(SearchResultItem(
            id=item["id"],
            categories=item.get("sourceCategories", []),
            properties={p["key"]: p["value"] for p in item.get("sourceProperties", [])}
        ))

    return items
