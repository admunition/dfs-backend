import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)
BASE_URL = "https://api.dataforseo.com/v3"


def _auth():
    return (settings.DATAFORSEO_USERNAME, settings.DATAFORSEO_PASSWORD)


async def _post(endpoint: str, payload: list) -> list | dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{endpoint}",
            auth=_auth(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"[DFS] {endpoint} → status: {data.get('status_code')}")
        if data.get("status_code") != 20000:
            logger.error(f"[DFS] Error: {data.get('status_message')}")
            return {"error": data.get("status_message")}
        return data["tasks"][0].get("result", [])


def _opportunity_score(volume: int, difficulty: int, competition: float) -> int:
    """Score from 0-100: high volume + low difficulty + low competition = high score."""
    vol_score = min(volume / 1000, 50)
    diff_score = max(0, (100 - difficulty) / 2)
    comp_penalty = competition * 10
    return max(0, min(100, int(vol_score + diff_score - comp_penalty)))


async def find_opportunities(
    niche: str, location: str, language: str, limit: int, user_id: str
) -> dict:
    # Step 1 — Keyword ideas from DataForSEO Labs
    kw_payload = [{
        "keywords": [niche],
        "location_name": location,
        "language_code": language,
        "limit": limit,
        "order_by": ["keyword_info.search_volume,desc"],
        # Correct filter format: array of arrays
        "filters": [["keyword_info.search_volume", ">", 100]],
    }]
    kw_result = await _post("/dataforseo_labs/google/keyword_ideas/live", kw_payload)

    if isinstance(kw_result, dict) and "error" in kw_result:
        return kw_result

    # DataForSEO Labs result: result[0]["items"] contains the keywords
    raw_items = []
    if isinstance(kw_result, list) and kw_result:
        raw_items = kw_result[0].get("items", [])
    logger.info(f"[DFS] Keyword ideas found: {len(raw_items)}")

    # Step 2 — YouTube SERP for top videos
    yt_payload = [{
        "keyword": niche,
        "location_name": location,
        "language_code": language,
        "block_depth": 10,
    }]
    yt_result = await _post("/serp/youtube/organic/live/advanced", yt_payload)

    # Step 3 — Score each keyword opportunity
    opportunities = []
    for item in raw_items:
        kw_info = item.get("keyword_info", {}) or {}
        kw_props = item.get("keyword_properties", {}) or {}
        volume = kw_info.get("search_volume") or 0
        difficulty = kw_props.get("keyword_difficulty") or 50
        competition = kw_info.get("competition") or 0.5
        cpc = kw_info.get("cpc") or 0
        score = _opportunity_score(volume, difficulty, competition)

        opportunities.append({
            "keyword": item.get("keyword", ""),
            "search_volume": volume,
            "keyword_difficulty": difficulty,
            "competition": round(competition, 2),
            "cpc": round(cpc, 2),
            "opportunity_score": score,
            "competition_level": kw_info.get("competition_level", "UNKNOWN"),
            "monthly_trend": kw_info.get("search_volume_trend", {}),
        })

    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Step 4 — Extract top YouTube videos
    # YouTube SERP result: result[0]["items"] contains the videos
    top_videos = []
    if isinstance(yt_result, list) and yt_result:
        yt_items = yt_result[0].get("items", [])
        for v in yt_items:
            if v.get("type") == "video" and len(top_videos) < 5:
                top_videos.append({
                    "title": v.get("title"),
                    "video_id": v.get("video_id"),
                    "channel": v.get("channel_name"),
                    "views": v.get("views_count"),
                    "url": v.get("url"),
                })

    logger.info(f"[DFS] Opportunities: {len(opportunities)}, Videos: {len(top_videos)}")

    return {
        "niche": niche,
        "total_opportunities": len(opportunities),
        "opportunities": opportunities[:limit],
        "top_youtube_videos": top_videos,
    }


async def get_trending(niche: str, language: str) -> dict:
    payload = [{
        "keywords": [niche],
        "language_code": language,
        "time_range": "past_30_days",
        "type": "web",
        "item_types": ["google_trends_graph", "google_trends_queries_list"],
    }]
    result = await _post("/keywords_data/google_trends/explore/live", payload)
    return {"niche": niche, "trends": result}


async def analyze_serp(q: str, location: str, language: str, depth: int) -> dict:
    payload = [{
        "keyword": q,
        "location_name": location,
        "language_code": language,
        "block_depth": depth,
    }]
    result = await _post("/serp/youtube/organic/live/advanced", payload)

    videos = []
    if isinstance(result, list) and result:
        for item in result[0].get("items", []):
            if item.get("type") == "video":
                videos.append({
                    "title": item.get("title"),
                    "video_id": item.get("video_id"),
                    "channel": item.get("channel_name"),
                    "views": item.get("views_count"),
                    "published_at": item.get("publication_date"),
                    "duration": item.get("duration"),
                    "url": item.get("url"),
                    "thumbnail": item.get("thumbnail_url"),
                    "description": (item.get("description") or "")[:300],
                })

    return {"keyword": q, "total_results": len(videos), "videos": videos}


async def analyze_video(video_id: str, location: str, language: str) -> dict:
    payload = [{
        "video_id": video_id,
        "location_name": location,
        "language_code": language,
    }]
    result = await _post("/serp/youtube/video_info/live/advanced", payload)

    if isinstance(result, list) and result:
        items = result[0].get("items", [])
        if items:
            v = items[0]
            return {
                "video_id": video_id,
                "title": v.get("title"),
                "channel": v.get("channel_name"),
                "views": v.get("views_count"),
                "likes": v.get("likes_count"),
                "comments": v.get("comments_count"),
                "published_at": v.get("publication_date"),
                "duration": v.get("duration"),
                "description": (v.get("description") or "")[:500],
                "tags": v.get("tags", []),
                "thumbnail": v.get("thumbnail_url"),
                "engagement_rate": round(
                    ((v.get("likes_count") or 0) / max(v.get("views_count") or 1, 1)) * 100, 2
                ),
            }
    return {"video_id": video_id, "error": "Video not found"}
