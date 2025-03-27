from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test_users() -> dict[str, str]:
    return {"msg": "Users endpoint is working!"}
