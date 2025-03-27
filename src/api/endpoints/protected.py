from fastapi import APIRouter, Depends
from src.api.dependencies.auth import get_current_user
from src.db.models import User
from src.api.schemas.user import UserRead

router = APIRouter(prefix="/protected", tags=["Protected"])

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead.from_orm(current_user)
