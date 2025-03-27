from fastapi import FastAPI

from src.api.endpoints import articles, auth, categories, protected, users

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


app.include_router(auth.router)
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(protected.router)
app.include_router(categories.router)
app.include_router(articles.router)
