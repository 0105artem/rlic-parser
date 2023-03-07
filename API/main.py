import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from db.config import engine, Base
from routers import license, user, auth, files, parser
from common.redis import redis_client, parsing_task
from settings import env

with open("./common/tags.json", "r", encoding='utf-8') as json_file:
    tags_metadata = json.load(json_file)

with open("./common/metadata.json", "r", encoding='utf-8') as json_file:
    metadata = json.load(json_file)

app = FastAPI(title=metadata[0]['title'], description=metadata[0]['description'], openapi_tags=tags_metadata)


@app.on_event("startup")
async def startup():
    # Prepare redis
    await redis_client.init_redis_connect()
    await parsing_task.init_hash()

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    await redis_client.close()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(license.router)
app.include_router(files.router)
app.include_router(auth.router)
app.include_router(parser.router)
app.include_router(user.router)


@app.get("/")
def root():
    return RedirectResponse(f"{env.HOSTNAME}/docs")
