from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api import routes
from app.core.config import get_settings

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="简单、可复用的名单抽奖器"
)

app.include_router(routes.router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(BASE_DIR / "templates" / "index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/healthz")
async def healthz():
    return {"status": "ok", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
