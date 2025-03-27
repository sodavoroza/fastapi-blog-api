from pydantic import BaseModel, ConfigDict
from typing import Optional

class ArticleCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[int] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None

class ArticleRead(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    category_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
