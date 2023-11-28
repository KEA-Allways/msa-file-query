import uvicorn
from fastapi  import HTTPException
from fastapi import FastAPI, Form 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from typing import Optional
from io import BytesIO
from typing import List
from pydantic import BaseModel
from pydantic import ValidationError
from dotenv import load_dotenv
from pymongo import MongoClient
import os

env_path = r'C:\Users\suha hwang\Desktop\projectPackage\FastAPI-BOOK\kaloTest\venv\.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")

mongo_client=MongoClient(MONGO_DB_URL)
db = mongo_client.file


class UserByPostFeignRequest(BaseModel):
    postSeq: int
    userSeq: int
    
#썸네일 반환 
@app.post("/receive_thumbnail_and_profile")
async def receive_thumbnail_and_profile(requests: List[UserByPostFeignRequest]):
    # MongoDB에서 해당 postSeq 값을 가진 문서 조회
    result_list = []
    for request  in requests:
        
        post_seq= request.postSeq
        user_seq = request.userSeq
        thumbnail = db.thumbnail.find_one({"postSeq":post_seq})
        user = db.user.find_one({"userSeq":user_seq})
        
        thumbImg = thumbnail.get("imageUrl","")
        profileImg=user.get("imageUrl","")
        result_object={"postSeq":post_seq,"userSeq":user_seq,"thumbImg":thumbImg,"profileImg":profileImg}
        result_list.append(result_object)
    #10개의 리스트 반환 
    return JSONResponse(content=result_list)

                                                                                                                             
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)