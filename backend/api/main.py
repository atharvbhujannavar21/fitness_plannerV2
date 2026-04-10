from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import ai, profiles, tasks
from rpc.server import serve


@asynccontextmanager
async def lifespan(_: FastAPI):
    import asyncio

    grpc_server = asyncio.create_task(serve())
    try:
        yield
    finally:
        grpc_server.cancel()


app = FastAPI(title="FitFusion API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
