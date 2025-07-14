from fastapi import FastAPI, Query, HTTPException, Request
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import requests
import json

app = FastAPI()

DMS_BASE_URL = "https://alpin-dev.d-velop.cloud/dms"  # Replace with real base URL
BEARER_TOKEN = "clz/cKSKWVF5NXa7poTS9RiN5S4QCGhjGxo0fE1QiB66qlfk1pGk3Pl5HFGT5y5IyW8c9jAMh7NefRWnFrT6FKLB3I06jTAE397KcEyPCnw=&_z_A0V5ayCTcDeHVN_zAEnmxEkZeE6im4OH05NlT0dh1poy0CbcKF_U1dq8-455l2Y3q4Sp-150HTIRGLRb_KTuaV5g0qQZW"  # Replace with your actual token

# Response models
class SearchResultItem(BaseModel):
    id: str
    title: Optional[str] = None
    properties: Dict[str, Any]

class SearchResponse(BaseModel):
    debug_url: str
    results: List[SearchResultItem]

@app.get("/search", response_model=SearchResponse)
def search_documents(
    request: Request,
    repository_id: str,
    objectdefinitionids: Optional[List[str]] = Query(..., description="List of document types (e.g. XAD04)"),
    properties: Optional[str] = Query(
        None,
        description='A JSON string of properties, e.g. {"property_document_id": ["UF00083745"]}'
    ),
    page: Optional[int] = 1,
    page_size: Optional[int] = 25
):
    # Build the query params for the real DMS API
    query_params = {
        "objectdefinitionids": json.dumps(objectdefinitionids),
        "page": page,
        "pageSize": page_size
    }

    if properties:
        try:
            props_dict = json.loads(properties)
            query_params["properties"] = json.dumps(props_dict)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in 'properties' parameter")

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    dms_url = f"{DMS_BASE_URL}/r/{repository_id}/sr/"

    try:
        response = requests.get(dms_url, headers=headers, params=query_params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"DMS search failed: {str(e)}")

    try:
        data = response.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid JSON returned by DMS")

    # Construct debug URL
    composed_url = f"{dms_url}?" + "&".join(
        f"{key}={requests.utils.quote(str(val))}" for key, val in query_params.items()
    )

    items = []
    for item in data.get("items", []):
        props = {
            p["key"]: p["value"]
            for p in item.get("properties", [])
        }
        items.append(SearchResultItem(
            id=item.get("id"),
            title=item.get("displayValue"),
            properties=props
        ))

    return SearchResponse(debug_url=composed_url, items=items)