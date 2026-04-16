from fastapi import APIRouter
from app.routes.example import router as example_router
from app.routes.seo import router as seo_router
from app.routes.youtube import router as youtube_router

router = APIRouter()

router.include_router(example_router, prefix="/example", tags=["Example"])
router.include_router(seo_router, prefix="/seo", tags=["SEO - DataForSEO"])
router.include_router(youtube_router, prefix="/youtube", tags=["YouTube - Opportunity Finder"])

# Add more routers here as your project grows:
# from app.routes.users import router as users_router
# router.include_router(users_router, prefix="/users", tags=["Users"])
