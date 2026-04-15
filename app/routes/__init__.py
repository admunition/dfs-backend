from fastapi import APIRouter
from app.routes.example import router as example_router

router = APIRouter()

router.include_router(example_router, prefix="/example", tags=["Example"])

# Add more routers here as your project grows:
# from app.routes.users import router as users_router
# router.include_router(users_router, prefix="/users", tags=["Users"])
