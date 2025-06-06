from fastapi import FastAPI, Query, File, UploadFile,HTTPException
from fastapi.responses import StreamingResponse,JSONResponse 
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.auth_middleware import auth_route
from .router.bot_route import router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(router);

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Application!"}