from fastapi import FastAPI, Query
from typing import Optional, List, Dict
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
    objectdefinitionids: List[str] = Query(...),
    properties: Optional[Dict[str, List[str]]] = None,
    page: int = 1,
    page_size: int = 25
):
    # Prepare query parameters as JSON-encoded strings
    query_params = {
        "objectdefinitionids": json.dumps(objectdefinitionids),
        "page": page,
        "pageSize": page_size
    }

    if properties:
        query_params["properties"] = json.dumps(properties)

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    search_url = f"{DMS_BASE_URL}/r/{repository_id}/sr/"

    try:
        response = requests.get(search_url, headers=headers, params=query_params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DMS search failed: {str(e)}")

    results = response.json()
    items = []

    for item in results.get("items", []):
        items.append(SearchResultItem(
            id=item["id"],
            title=item.get("displayValue"),
            properties={p["key"]: p["value"] for p in item.get("properties", [])}
        ))

    return items