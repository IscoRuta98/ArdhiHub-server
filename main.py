from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import authRouter
from routes.default import defaultRouter
from routes.records import recordsRouter
from routes.verify import verifyRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(defaultRouter, tags=["Entry Point"])
app.include_router(authRouter, tags=["Authentication"])
app.include_router(recordsRouter, tags=["Records"])
app.include_router(verifyRouter, tags=["Third Party Verification"])
