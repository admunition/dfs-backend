from fastapi import APIRouter, Depends, Query
from app.dependencies.auth import get_current_user
from app.controllers.youtube import (
    find_opportunities,
    get_trending,
    analyze_video,
    analyze_serp,
)

router = APIRouter()


@router.get("/opportunities")
async def opportunities(
    niche: str = Query(..., description="Niche or topic to search (e.g. 'cooking', 'fitness')"),
    location: str = Query("United States", description="Target location"),
    language: str = Query("en", description="Language code"),
    limit: int = Query(10, le=50),
    user: dict = Depends(get_current_user),
):
    """
    Find YouTube keyword opportunities in a niche.
    Returns keywords ranked by opportunity score (high volume + low competition).
    """
    return await find_opportunities(niche, location, language, limit, user["id"])


@router.get("/trending")
async def trending(
    niche: str = Query(..., description="Niche or topic"),
    language: str = Query("en"),
    user: dict = Depends(get_current_user),
):
    """Get trending topics and searches in a niche."""
    return await get_trending(niche, language)


@router.get("/analyze-serp")
async def serp(
    q: str = Query(..., description="YouTube search query"),
    location: str = Query("United States"),
    language: str = Query("en"),
    depth: int = Query(10, le=20),
    user: dict = Depends(get_current_user),
):
    """Get top YouTube videos ranking for a keyword with full metadata."""
    return await analyze_serp(q, location, language, depth)


@router.get("/analyze-video")
async def video(
    video_id: str = Query(..., description="YouTube video ID"),
    location: str = Query("United States"),
    language: str = Query("en"),
    user: dict = Depends(get_current_user),
):
    """Analyze a specific YouTube video — views, engagement, tags, description."""
    return await analyze_video(video_id, location, language)
