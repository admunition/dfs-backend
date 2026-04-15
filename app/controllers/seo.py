import httpx
from app.config import settings

BASE_URL = "https://api.dataforseo.com/v3"


def _auth():
    return (settings.DATAFORSEO_USERNAME, settings.DATAFORSEO_PASSWORD)


async def _post(endpoint: str, payload: list) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{endpoint}",
            auth=_auth(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("status_code") != 20000:
            return {"error": data.get("status_message")}
        return data["tasks"][0]["result"]


async def search_keywords(keyword: str, location: str, language: str, limit: int):
    payload = [{
        "keywords": [keyword],
        "location_name": location,
        "language_code": language,
    }]
    result = await _post("/dataforseo_labs/google/keyword_overview/live", payload)
    return {"keyword": keyword, "data": result}


async def get_serp_results(keyword: str, location: str, language: str, depth: int):
    payload = [{
        "keyword": keyword,
        "location_name": location,
        "language_code": language,
        "depth": depth,
    }]
    result = await _post("/serp/google/organic/live/advanced", payload)
    return {"keyword": keyword, "data": result}


async def get_backlinks(domain: str, limit: int):
    payload = [{
        "target": domain,
        "limit": limit,
    }]
    result = await _post("/backlinks/backlinks/live", payload)
    return {"domain": domain, "data": result}


async def get_domain_rank(domain: str, location: str, language: str):
    payload = [{
        "target": domain,
        "location_name": location,
        "language_code": language,
    }]
    result = await _post("/dataforseo_labs/google/domain_rank_overview/live", payload)
    return {"domain": domain, "data": result}


async def get_keyword_ideas(keyword: str, location: str, language: str, limit: int):
    payload = [{
        "keywords": [keyword],
        "location_name": location,
        "language_code": language,
        "limit": limit,
    }]
    result = await _post("/dataforseo_labs/google/keyword_ideas/live", payload)
    return {"keyword": keyword, "data": result}
