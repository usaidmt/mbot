# import imp
from fastapi import APIRouter, Depends, HTTPException
from fastapi import FastAPI, Query, File, UploadFile

from typing import List

from app.common import utils
from app.common.utils import allow_anonymous
from app.middleware.auth_middleware import auth_route
from ..core import bot_ai
from ..common import token
from ..model import request_model

# router = APIRouter(
#     prefix="/bot",
#     tags=["bot"]
# )

router = APIRouter(route_class=auth_route)


@router.post("/generate-token/")
@allow_anonymous
def generate_token(request: request_model.token_request):
    try:
        return token.generate_token(request)
    except Exception as e:
        raise HTTPException(status_code=500, exception=str(e))
    finally:
        pass


# REST API to create new collection
@router.get("/create_collection/")
async def create_collection(token: dict = Depends(utils._token)):
    try:
        para = { "user_code": token["user_code"] };
        data = utils.call_stored_procedure("sp_generate_collection", para);
        
        if not data or len(data) == 0:
            return None

        return await bot_ai.create_collection(data[0]['collection_name']);
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# REST API to handle uploaded files
@router.post("/feed_data/")
async def feed_data(file: UploadFile = File(...), token: dict = Depends(utils._token)):
    try:

        para = { "user_code": token["user_code"] };
        data = utils.call_stored_procedure("sp_get_collection", para);

        if not data or len(data) == 0:
            return None

        return await bot_ai.feed_data(data[0]['collection_name'], file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# REST API to handle queries and stream responses
@router.post("/generate_response/")
async def generate_response(request: request_model.generate_request):

    para = { "user_code": token["user_code"] };
    data = utils.call_stored_procedure("sp_get_collection", para);

    if not data or len(data) == 0:
        return None

    return await bot_ai.generate_response(
        collection_name=data[0]['collection_name'],
        prompt=request.prompt,
        language=request.language,
    )
