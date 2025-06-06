
from fastapi import FastAPI, Query, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from app.core.algorithm import bot_algo
from ..common import files_extract
from ..db import vector_db
import os
from dotenv import load_dotenv
from .algorithm import sql_bot_algo


import openai
import time
from chromadb import Client
from chromadb.config import Settings


load_dotenv()
openai.api_key = os.getenv("API_KEY")

allowed_extensions = ["txt", "pdf", "docx"]


# REST API to create new collection
async def create_collection(collection_name: str = Query(...)):
    try:
        return vector_db.create_collection(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# REST API to handle uploaded files
async def feed_data(collection_name, file):
    try:
        if not file:
            raise HTTPException(status_code=500, exception="No file uploaded.")

        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=500,
                exception=f"Unsupported file type: {file_extension}. Only txt, pdf, and docx are allowed.",
            )

        file_content = files_extract.read_file(file)
        # collection_name = "mt_collection" taking as a input para.. TS
        return vector_db.add_to_chroma(collection_name, file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# REST API to handle queries and stream responses
async def generate_response(
    collection_name: str = Query(...),
    prompt: str = Query(...),
    language: str = Query(...),
):
    try:

        # collection = vector_db.get_collection( os.getenv("DB_DIRECTORY"), collection_name );
        relevant_data = vector_db.query_chroma(collection_name, prompt, 10)
        # flattened = [item for sublist in relevant_data for item in sublist]
        # context = "\n".join(flattened)
        context = "\n".join(relevant_data)
        return StreamingResponse(
            bot_algo.generate_response(context, prompt=prompt, language=language),
            media_type="text/event-stream",
        )
    except Exception as e:
        return StreamingResponse(
            bot_algo.generate_response(
                context="", prompt="Reply with Something went wrong",language="English"
            ),
            media_type="text/event-stream",
        )
        raise HTTPException(status_code=500, exception=f"{str(e)}")


# async def stream_response(prompt: str = Query(...), language: str = Query(...)):
#     try:
#         return StreamingResponse(
#             sql_bot_algo.query_with_custom_data_only(prompt=prompt, language=language),
#             media_type="text/event-stream",
#         )
#     except Exception as e:
#         return StreamingResponse(
#             __query_with_custom_data_only("", prompt="Reply with Something went wrong"),
#             media_type="text/event-stream",
#         )
