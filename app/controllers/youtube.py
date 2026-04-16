import httpx
from app.config import settings

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
        if data.get("status_code") != 20000:
            return {"error": data.get("status_message")}
        return data["tasks"][0].get("result", [])


def _opportunity_score(volume: int, difficulty: int, competition: float) -> int:
    """
    Score an opportunity from 0-100.
    High volume + low difficulty + low competition = high score.
    """
    vol_score = min(volume / 1000, 50)           # max 50 pts from volume
    diff_score = max(0, (100 - difficulty) / 2)  # max 50 pts from low difficulty
    comp_penalty = competition * 10              # small penalty for competition
    return max(0, min(100, int(vol_score + diff_score - comp_penalty)))


async def find_opportunities(
    niche: str, location: str, language: str, limit: int, user_id: str
) -> dict:
    # Step 1: Get keyword ideas for the niche
    kw_payload = [{
        "keywords": [niche],
        "location_name": location,
        "language_code": language,
        "limit": limit,
        "order_by": ["keyword_info.search_volume,desc"],
        "filters": ["keyword_info.search_volume", ">", 100],
    }]
    kw_result = await _post("/dataforseo_labs/google/keyword_ideas/live", kw_payload)

    if isinstance(kw_result, dict) and "error" in kw_result:
        return kw_result

    # Step 2: Get YouTube SERP for the niche itself
    yt_payload = [{
        "keyword": niche,
        "location_name": location,
        "language_code": language,
        "block_depth": 5,
    }]
    yt_result = await _post("/serp/youtube/organic/live/advanced", yt_payload)

    # Step 3: Score each keyword opportunity
    opportunities = []
    items = kw_result if isinstance(kw_result, list) else []

    for item in items:
        kw_info = item.get("keyword_info", {})
        kw_props = item.get("keyword_properties", {})
        volume = kw_info.get("search_volume", 0) or 0
        difficulty = kw_props.get("keyword_difficulty", 50) or 50
        competition = kw_info.get("competition", 0.5) or 0.5
        cpc = kw_info.get("cpc", 0) or 0
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

    # Sort by opportunity score
    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Extract top YouTube videos for context
    top_videos = []
    if isinstance(yt_result, list) and yt_result:
        for block in yt_result[:3]:
            items_yt = block.get("items", [])
            for v in items_yt[:3]:
                if v.get("type") == "video":
                    top_videos.append({
                        "title": v.get("title"),
                        "video_id": v.get("video_id"),
                        "channel": v.get("channel_name"),
                        "views": v.get("views_count"),
                        "url": v.get("url"),
                    })

    return {
        "niche": niche,
        "total_opportunities": len(opportunities),
        "opportunities": opportunities[:limit],
        "top_youtube_videos": top_videos[:5],
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
    if isinstance(result, list):
        for block in result:
            for item in block.get("items", []):
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
                        "description": item.get("description", "")[:300],
                    })

    return {
        "keyword": q,
        "total_results": len(videos),
        "videos": videos,
    }


async def analyze_video(video_id: str, location: str, language: str) -> dict:
    payload = [{
        "video_id": video_id,
        "location_name": location,
        "language_code": language,
    }]
    result = await _post("/serp/youtube/video_info/live/advanced", payload)

    if isinstance(result, list) and result:
        video = result[0].get("items", [{}])[0]
        return {
            "video_id": video_id,
            "title": video.get("title"),
            "channel": video.get("channel_name"),
            "views": video.get("views_count"),
            "likes": video.get("likes_count"),
            "comments": video.get("comments_count"),
            "published_at": video.get("publication_date"),
            "duration": video.get("duration"),
            "description": video.get("description", "")[:500],
            "tags": video.get("tags", []),
            "thumbnail": video.get("thumbnail_url"),
            "engagement_rate": round(
                ((video.get("likes_count") or 0) / max(video.get("views_count") or 1, 1)) * 100, 2
            ),
        }
    return {"video_id": video_id, "error": "Video not found"}
