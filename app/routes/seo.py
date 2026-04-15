from fastapi import APIRouter, Depends, Query
from app.dependencies.auth import get_current_user
from app.controllers.seo import (
    search_keywords,
    get_serp_results,
    get_backlinks,
    get_domain_rank,
    get_keyword_ideas,
)

router = APIRouter()


@router.get("/keywords")
async def keywords(
    q: str = Query(..., description="Keyword to search"),
    location: str = Query("United States", description="Target location"),
    language: str = Query("en", description="Language code"),
    limit: int = Query(10, le=100),
    user: dict = Depends(get_current_user),
):
    """Get keyword data: search volume, CPC, competition, difficulty."""
    return await search_keywords(q, location, language, limit)


@router.get("/serp")
async def serp(
    q: str = Query(..., description="Search query"),
    location: str = Query("United States", description="Target location"),
    language: str = Query("en", description="Language code"),
    depth: int = Query(10, le=100),
    user: dict = Depends(get_current_user),
):
    """Get live Google SERP results for a keyword."""
    return await get_serp_results(q, location, language, depth)


@router.get("/backlinks")
async def backlinks(
    domain: str = Query(..., description="Target domain"),
    limit: int = Query(10, le=100),
    user: dict = Depends(get_current_user),
):
    """Get backlink data for a domain."""
    return await get_backlinks(domain, limit)


@router.get("/domain-rank")
async def domain_rank(
    domain: str = Query(..., description="Target domain"),
    location: str = Query("United States"),
    language: str = Query("en"),
    user: dict = Depends(get_current_user),
):
    """Get domain ranking overview and traffic estimates."""
    return await get_domain_rank(domain, location, language)


@router.get("/keyword-ideas")
async def keyword_ideas(
    q: str = Query(..., description="Seed keyword"),
    location: str = Query("United States"),
    language: str = Query("en"),
    limit: int = Query(10, le=100),
    user: dict = Depends(get_current_user),
):
    """Get keyword ideas based on a seed keyword."""
    return await get_keyword_ideas(q, location, language, limit)
